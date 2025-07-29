// ---------------------------------------------------------------------------------------------------------------------
// Copyright 2025 David Briant, https://github.com/coppertop-bones. All rights reserved.
// ---------------------------------------------------------------------------------------------------------------------

#ifndef __BK_OM_C
#define __BK_OM_C "bk/om.c"

#include <setjmp.h>
#include <string.h>
#include <limits.h>

#include "../../include/bk/bk.h"
#include "../../include/bk/om.h"
#include "lib/os.c"


pub BK_OM * OM_create(BK_MM *mm, BK_TM *tm) {
    BK_OM *om;  size_t sz;
    om = mm->malloc(sizeof(BK_OM));
    om->mm = mm;
    om->tm = tm;

    // reserve memory for blocks and bitmaps
    om->blocks = os_vm_reserve(0, OM_BLOCKS_SZ);
    os_mprotect(om->blocks, OM_BLOCKS_SZ, BK_PROT_READ | BK_PROT_WRITE);
    os_madvise(om->blocks, OM_BLOCKS_SZ, BK_MADV_RANDOM);

    sz = OM_SLOT_MAP_SZ + OM_LINE_MAP_SZ + OM_NUM_BLOCKS * sizeof(BK_OMAlloctor);
    om->obj_starts_bm = os_vm_reserve(0, sz);
    os_mprotect(om->obj_starts_bm, sz, BK_PROT_READ | BK_PROT_WRITE);
    os_madvise(om->obj_starts_bm, sz, BK_MADV_RANDOM);

    om->lines_bm = om->obj_starts_bm + OM_SLOT_MAP_SZ;
    om->allocators = (BK_OMAlloctor *)(om->obj_starts_bm + OM_SLOT_MAP_SZ + OM_LINE_MAP_SZ);

    // initialize allocators
    om->allocators[0].next_fresh = (OMSlot *)(om->blocks + OM_SLOT_SIZE);       // skip first slot as header is before our memory
    om->allocators[0].limit = (OMSlot *)(om->blocks + OM_BLOCK_SIZE - OM_OBJ_HEADER_SZ);
    om->allocators[0].next_recycled = om->allocators[0].limit;
    om->allocators[0].recycled_limit = om->allocators[0].limit;
    om->allocators[0].slot_count = 0;
    om->allocators[0].line_count = 0;

    for (int i=1; i < OM_NUM_BLOCKS; i++) {
        om->allocators[i].next_fresh = (OMSlot *)(om->blocks + OM_BLOCK_SIZE * i);
        om->allocators[i].limit = (OMSlot *)(om->blocks + OM_BLOCK_SIZE * (i + 1));
        om->allocators[i].next_recycled = om->allocators[i].limit;
        om->allocators[i].recycled_limit = om->allocators[i].limit;
        om->allocators[i].slot_count = 0;
        om->allocators[i].line_count = 0;
    }

    om->alloc_index = 0;
    om->medium_overflow_index = 1;
    return om;
}

pub int OM_trash(BK_OM *om) {
    os_vm_unreserve(om->obj_starts_bm, OM_SLOT_MAP_SZ + OM_LINE_MAP_SZ + OM_NUM_BLOCKS * sizeof(BK_OMAlloctor));
    os_vm_unreserve(om->blocks, OM_BLOCKS_SZ);
    free(om);
    return 0;
}


pvt void bm_set(u8 *bm, size i) {
    bm[i / 8] |= (1 << (i % 8));
}

pvt void bm_clear(u8 * bm, size i) {
    bm[i / 8] &= ~(1 << (i % 8));
}

pvt int bm_at(u8 const * bm, size i) {
    return bm[i / 8] & (1 << (i % 8));
}

void bm_set_range(u8 *bm, size_t i1, size_t i2) {
    size_t start_byte = i1 / 8;  size_t end_byte = i2 / 8;  size_t start_bit = i1 % 8;  size_t end_bit = i2 % 8;
    if (start_byte == end_byte) {
        bm[start_byte] |= ((1 << (end_bit - start_bit)) - 1) << start_bit;
        return;
    } else {
        bm[start_byte] |= 0xFF << start_bit;
    }
    for (size_t i = start_byte + 1; i < end_byte; i++) bm[i] = 0xFF;
    bm[end_byte] |= (1 << end_bit) - 1;
}

pvt void bm_clear_range(u8 *bm, size_t i1, size_t i2) {
    size_t start_byte = i1 / 8;  size_t end_byte = i2 / 8;  size_t start_bit = i1 % 8;  size_t end_bit = i2 % 8;
    if (start_byte == end_byte) {
        bm[start_byte] &= ~(((1 << (end_bit - start_bit)) - 1) << start_bit);
        return;
    } else {
        bm[start_byte] &= ~(0xFF << start_bit);
    }
    for (size_t i = start_byte + 1; i < end_byte; i++) bm[i] = 0x00;
    bm[end_byte] &= ~((1 << end_bit) - 1);
}

int bm_count_range(u8 *bm, size_t i1, size_t i2) {
    size_t start_byte = i1 / 8;  size_t end_byte = i2 / 8;  size_t start_bit = i1 % 8;  size_t end_bit = i2 % 8;
    int count = 0;
    if (start_byte == end_byte) {
        for (size_t bit = start_bit; bit < end_bit; bit++) {
            if (bm[start_byte] & (1 << bit)) {
                count++;
            }
        }
        return count;
    } else {
        for (size_t bit = start_bit; bit < 8; bit++) {
            if (bm[start_byte] & (1 << bit)) {
                count++;
            }
        }
    }
    for (size_t i = start_byte + 1; i < end_byte; i++) count += __builtin_popcount(bm[i]);
    for (size_t bit = 0; bit < end_bit; bit++) {
        if (bm[end_byte] & (1 << bit)) {
            count++;
        }
    }
    return count;
}

// BLOCK ALLOCATION
// each allocator lives is it's own thread and tracks it's free block count, the STW gc is responsible for
// adding to / reclaiming blocks from allocators - if an allocator runs out of blocks it can get a lock and then extra
// blocks or schedule a STW gc and block management.

// STICKY-IMMIX
// PhD p53 - Sticky MS and Sticky Immix are the non-moving generational variant of mark-sweep and Immix. Figure 4.9
// shows that our improved reference counting collector is only 1% slower than Sticky MS and 10% slower than Sticky Immix.

// object the chuck of allocation
// object-network - the object itself and child objects (e.g. a frame, an array of arrays)

// basic GC algorithm
// bump allocate objects and trace when no free blocks before making more blocks available from virtual memory

// space usage improvements
// 1) trace to find holes

// system improvements
// 1) defrag blocks and release back to OS
// 2) use lower part of heap so can release object map (and line map too but it's small fry x512 smaller in comparison)
//    back to OS (this is unlikely but consider the 104GB query that only allocates small and medium objects)

// defragment strategies
// evacuate first-time survivors
// evacuate survivors from fragmented block

// locality improvements
// 1) we can reduce overall cache misses by evacuating individual objects in fragmented blocks into a more compact area
// 2) we can reduce individual object-network cache misses by moving it into a contiguous space
// 3) we can reduce cache misses of recently used objects by tracing the scratch area and using its allocation

// trace performance improvements
// 1) trace subset of a space (i.e. trace the nursary generation) - the line map of a parent generation can be copied
//    as the starting point for its child generation
// 2) objects can be moved from generation to its parent by marking its generation id

// it should be exceedingly rare to need to defrag or compact large object virtual memory

// out of memory is a design decision
// - for first cut we will not implement defragmentation of large object blocks nor compaction of large object virtual memory


// when searching for holes we could return the n largest and fill holes into the smallest that fits
// the decision to allocate into overflow seems to indicate that the immix authors preferred to rely on evacuation
// rather than hole filling


// MOVINB
// all objects on a page that are not pinned can be copied elsewhere, tombestoned then a trace performed to change
// pointers to tombstones to pointers to the new location of the moved object


pvt int om_new_overflow(BK_OM *om) {
    // we can't allocate into current alloc_index at the next_recycled but that doesn't mean there isn't space
    return 0;                                                                   // not yet implemented
}

pub void * om_alloc(BK_OM *om, size szInSlots, btypeid_t btypeid, int rc) {
    // answer a pointer to a newly allocated object, lines are not marked as used, object start is set, for example:
    //     int sz = tm_size(om->tm, btypeid, 0);        om, type, variable_part_count
    //     void *p = om_alloc(om, 1 + sz / OM_SLOT_SIZE, btypeid, 0);

    void *answer;  BK_OMAlloctor *alloc;  u32 typeRcAndFlags, iLine;  u32 objSizeMask, blockStartInLines;
    bool isSmall, skipComplete;  mem blockStart;

    alloc = om->allocators + om->alloc_index;

    if (OM_MEDIUM_OBJ_SLOT_MAX < szInSlots) {
        // large object
        return 0;
    }
    objSizeMask = (szInSlots <= OM_SMALL_OBJ_SLOT_MAX) ? OM_IS_SMALL : OM_IS_MEDIUM;
    if ((alloc->next_fresh + szInSlots) < alloc->limit) {
        answer = alloc->next_fresh;             // alloc small or medium into fresh memory
        alloc->next_fresh += szInSlots;
    }
    else if ((alloc->next_recycled + szInSlots) < alloc->recycled_limit) {
        answer = alloc->next_recycled;          // alloc small or medium into recycled memory
        alloc->next_recycled += szInSlots;
        memset((mem) answer, 0, szInSlots * OM_SLOT_SIZE - OM_OBJ_HEADER_SZ);   // zero as using recycled memory
    }
    else if (szInSlots <= OM_SMALL_OBJ_SLOT_MAX) {
        // efficiently skip to next allocatable line (i.e. last in run of used lines + 2), alloc small into recycled
        // memory and track stats
        blockStartInLines = OM_LINES_PER_BLOCK * om->alloc_index;
        blockStart = om->blocks + blockStartInLines * OM_SLOT_SIZE;
        iLine = ((mem) alloc->next_fresh - blockStart) / OM_SLOT_SIZE + 1;
        skipComplete = false;
        while (!skipComplete) {
            while (bm_at(om->lines_bm, iLine) && iLine < OM_LINES_PER_BLOCK) iLine++;   // find the next free line

            if (iLine < OM_LINES_PER_BLOCK - 1) {
                // find the hole's limit
            }
            else if (iLine == OM_LINES_PER_BLOCK - 1) {
                // using last line

                skipComplete = true;
            }
            else {
                // block full, get a new block
                skipComplete = true;
                return 0;                                                       // not yet implemented
            }
        }
        objSizeMask = OM_IS_SMALL;
    }
    else {

    }

    // OPEN: if medium use overflow (handling out of blocks), if small skip (tracking reallocation wastage) to next
    // free whole line, if no free whole lines, get next partial block, (store the recycle count of a block, a block
    // that has been recycled a lot is likely a good candidate for evacuation as it is likely to be temporarily
    // fragmented). if no recyclable blocks then fresh bloc. in unlikely event of no fresh blocks, aggressively get a
    // new block, if none then, emergency GC nursary, if still none then emergengy GC all, if still none then we are really out of memory.

    // so "out of memory" is a design decision and really a warning - as we can always get more memory from the OS
    // even if it is in swap.

//    // contiguous allocation increases locality -
//    else if (((alloc = om->allocators + om->overflow_index)->next_fresh + szInSlots) < alloc->limit) {
//        // fresh, overflow alllocator (we don't use recycled memory for overflow)
//        // fresh, main alllocator
//        answer = alloc->next_fresh;
//        alloc->next_fresh += szInSlots;
//    } else {
//
//        // we can't allocate into current alloc_index at the next_recycled but that doesn't mean there isn't space
//        // we can try to find a hole that is big enough in the current block, or in another block, or get a new
//        // try getting a new overflow block
//        if (om_new_overflow(om)) {
//            // fresh, overflow alllocator (we don't use recycled memory for overflow)
//            // fresh, main alllocator
//            answer = alloc->next_fresh;
//            alloc->next_fresh += szInSlots;
//        } else {
//            // try to find a gap in this block with enough unused lines
//            // (it may be that we run into fresh memory - which is okay but needs handling
//            // if we can't find a gap then try to find a gap in another block (is this different for small and medium allocators?)
//            // if we can't find a gap in any block then we are in dire straits as the OM should have already compacted before we got here
//            //      flag out of memory and longjmp to failure handler
//            return 0;                                                               // not yet implemented
//        }
//    }
    // update OM data
    typeRcAndFlags = (btypeid & OM_BTYPEID_MASK);
    typeRcAndFlags |= objSizeMask;                                              // obj size flag
    typeRcAndFlags |= (rc > OM_MAX_RC ? OM_MAX_RC : rc) << OM_RC_SHIFT;         // rc
    memcpy((u32 *) answer - 1, &typeRcAndFlags, sizeof(u32));                   // obj header
    bm_set(om->obj_starts_bm, ((mem) answer - om->blocks) / OM_SLOT_SIZE);      // obj start
    alloc->slot_count += szInSlots;                                             // slot count
    return answer;
}

pub void * om_realloc(BK_OM *om, void *mutableObj, size oldSzInSlots, size newSzInSlots) {
    // if object cannot be grown then returns 0 and client will have to allocate a new object and copy the data
    // if object is being shrunk from medium to small isSmallFlag change
    // typically usage is to shrink large objects to release memory to OS
    return 0;                                                                   // not yet implemented
}

pvt void move_obj(mem old_location, mem new_location, size szInSlots) {
    // move object from one location to another leaving a tombstone in the old location
    // if the object is being moved to a different block then the object start is updated
}

pub u32 om_count(BK_OM *om, void *p) {
    u32 *header;
    header = (u32 *)p - 1;
    return *header & OM_RC_MASK;
}

pub u32 om_dup(BK_OM *om, void *p) {
    u32 n; i32 *header, nNew;
    header = (u32 *)p - 1;
    nNew = *header & OM_RC_MASK + OM_ONE_RC;
    n = nNew > OM_MAX_RC ? OM_MAX_RC : nNew;
    *header = *header & OM_RC_UNMASK | n;
    return n;
}

pub u32 om_drop(BK_OM *om, void *p) {
    // decrement the ref count, destroying the object if zero, return the new ref count
    u32 n; i32 *header, nNew;
    header = (u32 *)p - 1;
    nNew = *header & OM_RC_MASK - OM_ONE_RC;
    if (nNew == 0) {
        return om_free(om, p);
    } else {
        *header = *header & OM_RC_UNMASK | nNew;
        return n;
    }
}

pub u32 om_temporarily_deref(BK_OM *om, void *p) {
    // decrement the reference count and return the new value. Take no additional action if the new value is 0.
    u32 n; i32 *header, nNew;
    header = (u32 *)p - 1;
    nNew = *header & OM_RC_MASK - OM_ONE_RC;
    *header = *header & OM_RC_UNMASK | nNew;
    return n;
}

pub u32 om_free(BK_OM *om, void *p) {
    // remove object from map, free line if last, decrement references, call finaliser if needed
    u32 n; i32 *header, nNew;
    header = (u32 *)p - 1;
    *header & OM_RC_MASK;
    // check size and take appropriate action
    return 0; // not yet implemented

    return *header & OM_BTYPEID_MASK;
}


pub btypeid_t inline om_btypeid(BK_OM *om, void *p) {
    u32 n; i32 *header, nNew;
    header = (u32 *)p - 1;
    return *header & OM_BTYPEID_MASK;
}

pub int om_mark_line(BK_OM *om, void *p) {
    return 0;
}

//pub int om_is(BK_OM *om, void *p) {
//    // answer true if p points to the start of an object
//    if (p < om->blocks || om-> <= p) return 0;
//    // OPEN: check the slot table
//    return 1;
//}
//
//pub int om_is_within(BK_OM *om, void *p) {
//    if (p < om->blocks || om->endOf <= p) return 0;
//    // OPEN: implment
//    // if this line == 0 and this line - 1 == 0 return 0;
//    // scan back up to OM_LARGE_OBJECT_SIZE if no slot return 0;
//    // get size from type if p > size return 0;
//    return 1;
//}

#endif      // __BK_OM_C


