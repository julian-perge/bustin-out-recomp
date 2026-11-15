struct Vec3_00018790
{
    float x, y, z;
};

struct C_00018790
{
    char m_pad[0x12c];
    Vec3_00018790 m_12c;
    void fn_00018790(Vec3_00018790 v);
};

// 0x00018790
void C_00018790::fn_00018790(Vec3_00018790 v)
{
    m_12c = v;
}
