struct C_000D20E0
{
    char m_pad[0x344];
    float m_344, m_348, m_34c;
    void fn_000D20E0(float x, float y, float z);
};

// 0x000D20E0
void C_000D20E0::fn_000D20E0(float x, float y, float z)
{
    m_344 = x;
    m_348 = y;
    m_34c = z;
}
