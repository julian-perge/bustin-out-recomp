#include "UnkTargetBase.h"

// The node of the child list: the child at +0x0 and the next node at +0x8.
struct ChildNode_00124680
{
    UnkTargetBase* child;
    int unk4;
    ChildNode_00124680* next;
};

// 0x00124680
void UnkTargetBase::FUN_00124680(unsigned int bits, bool set)
{
    SetFlags(bits, set);
    ChildNode_00124680* node = *(ChildNode_00124680**)children;
    for (; node; node = node->next) {
        node->child->FUN_00124680(bits, set);
    }
}
