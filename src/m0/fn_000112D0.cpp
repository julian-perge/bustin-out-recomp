struct Element_000112D0
{
};

typedef void (Element_000112D0::*Init_000112D0)();

// 0x000112D0
void __stdcall fn_000112D0(char* items, unsigned int stride, int count,
                           Init_000112D0 init)
{
    while (--count >= 0)
    {
        (reinterpret_cast<Element_000112D0*>(items)->*init)();
        items += stride;
    }
}
