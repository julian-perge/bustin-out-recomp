struct S_0018E450
{
    int x;
    int y;
    S_0018E450& fn_0018E450(const S_0018E450& o);
};
// 0x0018E450
S_0018E450& S_0018E450::fn_0018E450(const S_0018E450& o)
{
    y += o.y;
    x += o.x;
    return *this;
}
