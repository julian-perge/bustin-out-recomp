struct Target_001695F0
{
    virtual void s000();
    virtual void Notify(int value, int state);
};

struct C_001695F0
{
    int m_0;
    int m_4;
    Target_001695F0* m_target;
    int m_value;
    void fn_001695F0(Target_001695F0* target, int a, int b);
};

// 0x001695F0
void C_001695F0::fn_001695F0(Target_001695F0* target, int a, int b)
{
    if (target == m_target)
        target->Notify(m_value, 0);
    if (m_target)
        target->Notify(0, 2);
    m_0 = a;
    m_4 = b;
    m_target = target;
    target->Notify(m_value, 1);
}
