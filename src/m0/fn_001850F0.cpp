struct S_001850F0
{
    char m_pad[0xb0];
    unsigned int m_b0[9];
    unsigned int m_d4;
};

// 0x001850F0
void fn_001850F0(S_001850F0* s, unsigned int a, unsigned int b, unsigned int c,
                 unsigned int d)
{
    s->m_b0[s->m_d4 & 0xff] = (((a << 4 | d) << 4 | b) << 4) | c;
}
