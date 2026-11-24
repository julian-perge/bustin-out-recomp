extern "C" double sqrt(double);

struct S_00035700
{
    float x;
    float y;
    float FUN_00035700();
};

// 0x00035700
float S_00035700::FUN_00035700()
{
    return (float)sqrt(x * x + y * y);
}
