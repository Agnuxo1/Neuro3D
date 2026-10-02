// Opt-in integer-only SOURCE hi-lo -> binary64 words. NOT compiled/executed.
// Caller GLSL >=400 concatenates frozen axial_native_signed512_v1.glsl FIRST.
// MODEL axial-SOURCE-zero-aware-integer-words-GLSL-v1
// Caller MUST propagate false; failure output is INVALID, never a zero result.
// No frame parser, SHA/authentication, scene admission, main(), binding or dispatch.
#ifndef EXP005_SOURCE_ZERO_AWARE_INTEGER_V1
#define EXP005_SOURCE_ZERO_AWARE_INTEGER_V1
#ifndef EXP005_SIGNED512_V1
#error frozen_signed512_header_required_first
#endif
bool exp005_source_word32_selected_v1(uint w) {
    uint e=(w>>23u)&255u, m=w&0x7fffffu;
    return e!=255u && (e!=0u || m==0u);
}
uint exp005_source_mag_bit_v1(Exp005I512 a, int bit) {
    return (a.w[bit/32]>>(uint(bit)%32u))&1u;
}
bool exp005_source_mag_round64_v1(Exp005I512 mag, uint sign32, out uvec2 words) {
    words=uvec2(0u);
    if((sign32&0x7fffffffu)!=0u || exp005_neg512(mag)) return false;
    int top=-1;
    for(int bit=511;bit>=0;--bit) {
        if(exp005_source_mag_bit_v1(mag,bit)!=0u) { top=bit; break; }
    }
    // Bound for sums of TWO selected binary32 values scaled by 2^149.
    if(top>277) return false;
    if(top<0) { words=uvec2(0u,sign32); return true; }
    uvec2 sig=uvec2(0u);
    for(int j=0;j<53;++j) {
        int src=top-j, dst=52-j;
        uint b=src>=0 ? exp005_source_mag_bit_v1(mag,src) : 0u;
        if(dst<32) sig.x|=b<<uint(dst);
        else sig.y|=b<<uint(dst-32);
    }
    int cut=top-52;
    bool roundUp=false;
    if(cut>0) {
        bool guardBit=exp005_source_mag_bit_v1(mag,cut-1)!=0u, sticky=false;
        for(int bit=0;bit<cut-1;++bit) {
            if(exp005_source_mag_bit_v1(mag,bit)!=0u) sticky=true;
        }
        roundUp=guardBit && (sticky || (sig.x&1u)!=0u);
    }
    if(roundUp) {
        uint old=sig.x; sig.x+=1u; if(sig.x<old) sig.y+=1u;
        if((sig.y&0x00200000u)!=0u) {
            sig=uvec2((sig.x>>1u)|(sig.y<<31u),sig.y>>1u);
            top+=1;
        }
    }
    // exact decoded magnitude is mag*2^-149; IEEE exponent is top-149+1023.
    words=uvec2(sig.x,sign32|(uint(top+874)<<20u)|(sig.y&0x000fffffu));
    return true;
}
bool exp005_source_hilo_zeroaware_words_v1(uvec2 limbs, out uvec2 words) {
    words=uvec2(0u);
    // BOTH inputs before ANY frozen decode; malformed second limb cannot produce output.
    if(!exp005_source_word32_selected_v1(limbs.x) ||
       !exp005_source_word32_selected_v1(limbs.y)) return false;
    if((limbs.x&0x7fffffffu)==0u && (limbs.y&0x7fffffffu)==0u) {
        words=uvec2(0u,limbs.x&0x80000000u); return true;
    }
    Exp005I512 sum;
    if(!exp005_decode_hilo512(limbs,sum)) return false;
    uint sign32=exp005_neg512(sum) ? 0x80000000u : 0u;
    Exp005I512 mag=sum;
    if(sign32!=0u) mag=exp005_negmod512(sum);
    // Exact cancellation of NONZERO limbs selects +0; only both-zero uses HIGH sign.
    return exp005_source_mag_round64_v1(mag,sign32,words);
}
#endif
