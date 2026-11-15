struct C_001F8860
{
    virtual void s000();
    virtual void s001();
    virtual int Load(void* item);
    virtual int Check(void* item);
    virtual int Open(void* item);
    int fn_001F8860(void* item, unsigned char flags);
};

// 0x001F8860
int C_001F8860::fn_001F8860(void* item, unsigned char flags)
{
    int result;
    if (flags & 2)
    {
        result = Check(item);
        if (result != -40)
            return result;
        result = Load(item);
        if (result != 0)
            return result;
    }
    result = Open(item);
    if (result != 0 && (flags & 1))
    {
        result = Load(item);
        if (result == 0)
            result = Open(item);
    }
    return result;
}
