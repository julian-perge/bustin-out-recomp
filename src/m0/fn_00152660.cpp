struct Stream_00152660
{
    virtual void s000();
    virtual void s001();
    virtual void s002();
    virtual void s003();
    virtual void s004();
    virtual void Write(const void* data, int size);
    void WriteFloat(float value)
    {
        Write(&value, 4);
    }
};

struct Vec3_00152660
{
    float x, y, z;
};

// 0x00152660
Stream_00152660& fn_00152660(Stream_00152660& stream, const Vec3_00152660& v)
{
    float z = v.z;
    float y = v.y;
    float x = v.x;
    stream.WriteFloat(x);
    stream.WriteFloat(y);
    stream.WriteFloat(z);
    return stream;
}
