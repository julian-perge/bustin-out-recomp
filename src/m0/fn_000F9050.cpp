inline void* operator new(unsigned int, void* where)
{
    return where;
}

struct Vec3_000F9050
{
    float x, y, z;
    Vec3_000F9050(const Vec3_000F9050& other) : x(other.x), y(other.y), z(other.z)
    {
    }
};

struct Matrix_000F9050
{
    float m[16];
};

struct Element_000F9050
{
    Vec3_000F9050 m_position;
    Matrix_000F9050 m_transform;
};

// 0x000F9050
Element_000F9050* fn_000F9050(Element_000F9050* first, Element_000F9050* last,
                              Element_000F9050* dest)
{
    for (; first != last; ++first, ++dest)
        new (dest) Element_000F9050(*first);
    return dest;
}
