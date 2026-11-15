extern "C" int __cdecl strcmp(const char* a, const char* b);

struct Name_001A5150
{
    const char* m_text;
    int fn_001A5150(const Name_001A5150& other) const;
};

// 0x001A5150
int Name_001A5150::fn_001A5150(const Name_001A5150& other) const
{
    return strcmp(m_text, other.m_text);
}
