#include "m0_slots.h"

struct Data_00085FB0
{
    int* m_items;
    int Count() const
    {
        return m_items ? m_items[-1] : 0;
    }
    int operator[](int index) const
    {
        return m_items[index];
    }
};

struct Info_00085FB0
{
    char m_pad[0xc0];
    Data_00085FB0* m_data;
};

struct Object_00085FB0
{
    M0_SLOTS_107
    virtual Info_00085FB0* GetInfo();
};

// 0x00085FB0
int fn_00085FB0(Object_00085FB0* object)
{
    if (object && object->GetInfo() && object->GetInfo()->m_data &&
        object->GetInfo()->m_data->Count() > 0 &&
        (*object->GetInfo()->m_data)[0] == (int)0xbfb9ee2a)
        return 1;
    return 0;
}
