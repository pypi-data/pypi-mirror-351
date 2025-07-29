// ---------------------------------------------------------------------------------------------------------------------
// Copyright 2025 David Briant, https://github.com/coppertop-bones. All rights reserved.
//
// OM - OBJECT MANAGER - an immix style memory manager - conservative on stack, precise on heap with CoW ref counting
// ---------------------------------------------------------------------------------------------------------------------

#ifndef INC_BK_OM_H
#define INC_BK_OM_H "bk/om.h"

#include "bk.h"
#include "mm.h"
#include "tm.h"


#define OM_OBJ_HEADER_SZ 4
#define OM_SLOT_SIZE 16
#define OM_LINE_SIZE 256
#define OM_SMALL_OBJ_SIZE OM_LINE_SIZE
#define OM_LARGE_OBJ_SIZE _8K
#define OM_BLOCK_SIZE _32K

#define OM_SMALL_OBJ_SLOT_MAX 16        /* OM_SMALL_OBJ_SIZE / OM_SLOT_SIZE */
#define OM_MEDIUM_OBJ_SLOT_MAX 512      /* OM_LARGE_OBJ_SIZE / OM_SLOT_SIZE */

#define OM_SLOT_MAP_SZ_PER_BLOCK 256
#define OM_LINE_MAP_SZ_PER_BLOCK 16


// OBJECT HEADER

#define OM_SIZE_MASK            0x80000000      /* 0 for small, 1 for medium, large live in different address spaces */
#define OM_IS_SMALL             0x00000000
#define OM_IS_MEDIUM            0x80000000
#define OM_GEN_ID               0x40000000      /* 0 for nursary, 1 for mature, can be extended to more later if necessary */
#define OM_PIN_COLOR_UNMASK     0xCFFFFFFF      /* header & OM_PIN_COLOR_UNMASK | OM_PIN_RED_MASK */
#define OM_PIN_COLOR_MASK       0x30000000
#define OM_PIN_RED              0x30000000
#define OM_PIN_GREEN            0x20000000
#define OM_PIN_BLUE             0x10000000
#define OM_NO_PIN               0x00000000
#define OM_HAS_FINALISER_MASK   0x08000000
#define OM_IS_VARIABLE_MASK     0x04000000      /* also in type */
#define OM_IS_DEEP_MASK         0x03000000
#define OM_IS_PTR_MASK          0x02000000      /* also in type */
#define OM_HAS_PTR_MASK         0x01000000      /* also in type */
#define OM_RC_MASK              0x00F00000      /* 4-bits */
#define OM_RC_UNMASK            0xFF0FFFFF      /* 4-bits */
#define OM_BTYPEID_MASK         0x000FFFFF      /* 20-bits at least up to 1,048,576 types */
#define OM_ONE_RC               0x00100000
#define OM_MAX_RC               0x00F00000
#define OM_RC_SHIFT             20

#define OM_SCRATCH              0
#define OM_NURSERY              1
#define OM_GLOBAL               2


typedef struct {        // tombstone must fit within the smallest object size - 12 bytes
    void *ptr;          // 8
    u32 sizeInLInes;    // 4
} OMTombstone;


typedef struct {
    u8 bytes[OM_SLOT_SIZE];
} OMSlot;

typedef struct {
    u8 bytes[OM_LINE_SIZE];
} OMLine;

typedef struct {
    OMSlot *next_recycled;
    OMSlot *recycled_limit;
    OMSlot *next_fresh;
    OMSlot *limit;
    u16 slot_count;     // max 2048
    u8 line_count;      // max 128
    u32 flags;          // isEvacuating, hasSpareSmall, hasSpareMedium
} BK_OMAlloctor;

typedef struct _BK_OMSpace {
    void **block_starts;
    size block_starts_sz;
    void **pins;
    size pins_sz;
    struct _BK_OMSpace *elder;
    struct _BK_OMSpace *younger;
} BK_OMSpace;

typedef struct {
    BK_MM *mm;
    BK_TM *tm;
    char *blocks;
    u8 *obj_starts_bm;
    u8 *lines_bm;
    BK_OMAlloctor *allocators;
    // do we need 6 allocators? for scratch, nursery and global?
    u32 alloc_index;
    u32 medium_overflow_index;
    void **roots;
    int trace_colour;   // red, green, blue, white
} BK_OM;

pub BK_OM * OM_create(BK_MM *, BK_TM *);
pub int OM_trash(BK_OM *);

pub void * om_alloc(BK_OM *, size szInSlots, btypeid_t, int rc);
pub void * om_realloc(BK_OM *om, void *mutableObj, size oldSzInSlots, size newSzInSlots);
tdd u32 om_count(BK_OM *, void *);
pub u32 om_dup(BK_OM *, void *);
pub u32 om_drop(BK_OM *, void *);
pub u32 om_free(BK_OM *, void *);
// om_copy, om_reuse, om_unique


pub btypeid_t om_btypeid(BK_OM *, void *);
pub bool om_is_obj(BK_OM *, void *);
pub void * om_in_obj(BK_OM *, void *);
pub int om_pin(BK_OM *, void *);
pub int om_unpin(BK_OM *, void *);
pub int om_is_pinned(BK_OM *, void *);
pub int om_needs_finalising(BK_OM *, void *);

pub void ** om_conservative_roots();      // answers a list of object (i.e. void *) that are conservatively pinned
pub void ** om_generation_roots(BK_OM *, BK_OMSpace *);      // answers a list of object (i.e. void *) that are conservatively pinned

// various traces
void om_keep_alive_trace(BK_OM *, void *roots);
// om_trace_reset_ref_counts
// om_move_objects_to_parent_trace((BK_OM *, void *roots, BK_OMSpace *parent);

#define OM_BLOCKS_SZ_FOR_128GB_SM_HEAP _128GB
#define OM_SLOT_MAP_SZ_FOR_128GB_SM_HEAP _2GB
#define OM_LINE_MAP_SZ_FOR_128GB_SM_HEAP _64M
#define OM_NUM_BLOCKS_FOR_128GB_SM_HEAP _16M

#define OM_NUM_PAGES_FOR_1TB_L_HEAP _256M

#define OM_BLOCKS_SZ OM_BLOCKS_SZ_FOR_128GB_SM_HEAP
#define OM_SLOT_MAP_SZ OM_SLOT_MAP_SZ_FOR_128GB_SM_HEAP
#define OM_LINE_MAP_SZ OM_LINE_MAP_SZ_FOR_128GB_SM_HEAP
#define OM_NUM_BLOCKS OM_NUM_BLOCKS_FOR_128GB_SM_HEAP
#define OM_LINES_PER_BLOCK 128
#define OM_SLOTS_PER_BLOCK _2K

#define OM_NUM_PAGES_FOR_L_HEAP OM_NUM_PAGES_FOR_1TB_L_HEAP


#endif // INC_BK_OM_H
