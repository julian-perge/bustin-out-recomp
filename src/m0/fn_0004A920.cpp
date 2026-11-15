struct Base_0004A920
{
    virtual void s000();
};

struct Lock_0004A920
{
    virtual void s000();
    virtual void Enter(int timeout);
    virtual void s002();
    virtual void Leave();
};

struct C_0004A920 : Base_0004A920, Lock_0004A920
{
    char m_pad[0x8c - 8];
    int m_8c;
    void fn_0004A920();
};

// 0x0004A920
void C_0004A920::fn_0004A920()
{
    Enter(-1);
    m_8c++;
    Leave();
}
