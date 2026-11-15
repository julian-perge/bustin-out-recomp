extern float DAT_002e21ac;

struct S_00050620
{
    char pad[0xD8];
    bool flag;
    char pad2[3];
    float value;
    void fn_00050620();
};

// 0x00050620
void S_00050620::fn_00050620()
{
    float v = DAT_002e21ac;
    flag = true;
    value = v;
}
