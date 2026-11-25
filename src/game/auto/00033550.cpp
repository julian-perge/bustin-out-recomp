extern "C" char* strcpy(char*, const char*);

// 0x00033550
void __stdcall GetInitLightsHelpText(char* out)
{
    strcpy(out, "InitLights: L = Hot Sync -- R = ReCompute");
}
