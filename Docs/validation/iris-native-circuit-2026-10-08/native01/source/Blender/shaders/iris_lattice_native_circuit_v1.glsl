#version 450 core
#extension GL_ARB_gpu_shader_fp64 : require
#pragma optimize(on)
#pragma optionNV(unroll none)
layout(local_size_x=1,local_size_y=1,local_size_z=1) in;
layout(std140,binding=0) uniform CircuitPacket { uvec4 packet[2048]; };
layout(r32ui,binding=0) uniform writeonly uimage2D input_echo;
layout(r32ui,binding=1) uniform writeonly uimage2D results;
uniform int nonce;

const double PI=3.141592653589793238462643383279502884LF;
const double LN2=0.693147180559945309417232121458176568LF;
uint word(int index) { return packet[index/4][index%4]; }
double scalar(int offset,int index) { int p=offset+2*index;return packDouble2x32(uvec2(word(p),word(p+1))); }
void put(int index,uint value) { imageStore(results,ivec2(index%64,index/64),uvec4(value,0,0,0)); }
void number(int index,double value) { uvec2 w=unpackDouble2x32(value);put(index,w.x);put(index+1,w.y); }
dvec2 multiply(dvec2 a,dvec2 b) { return dvec2(a.x*b.x-a.y*b.y,a.x*b.y+a.y*b.x); }
dvec2 times_i(dvec2 a) { return dvec2(-a.y,a.x); }

dvec2 phase(double angle) {
    double x=angle-floor(angle/(2.0LF*PI)+0.5LF)*(2.0LF*PI);
    double square=x*x;
    double sine=x,cosine=1.0LF,st=x,ct=1.0LF;
    for(int n=1;n<32;++n) {
        st*=-square/(double(2*n)*double(2*n+1));
        ct*=-square/(double(2*n-1)*double(2*n));
        sine+=st;cosine+=ct;
    }
    return dvec2(cosine,sine);
}

double exponential(double x) {
    int exponent=int(floor(x/LN2+0.5LF));double r=x-double(exponent)*LN2;
    double sum=1.0LF,term=1.0LF;
    for(int n=1;n<32;++n) { term*=r/double(n);sum+=term; }
    return ldexp(sum,exponent);
}

void main() {
    int words=int(word(3)),samples=int(word(4));
    int echo_words=((words+63)/64)*64;
    for(int p=0;p<echo_words;++p) imageStore(input_echo,ivec2(p%64,p/64),uvec4(word(p),0,0,0));
    int features=int(word(5)),theta=int(word(6)),scaler=int(word(7));
    int reference=int(word(8)),gain_offset=int(word(9)),geometry=int(word(10));
    double wavelength=scalar(geometry,0),gap=scalar(geometry,1),spacing=scalar(geometry,2);
    double kw=2.0LF*PI/wavelength,bs=1.0LF/sqrt(2.0LF);
    double ref=scalar(reference,0),gain=exponential(scalar(gain_offset,0));
    double X[4],Y[4];X[0]=0.0LF;Y[0]=0.0LF;
    for(int i=1;i<4;++i) {
        double index=double(i);
        X[i]=X[i-1]+spacing+scalar(geometry,3)*index+scalar(geometry,4)*index*index;
        Y[i]=Y[i-1]+spacing+scalar(geometry,5)*index+scalar(geometry,6)*index*index;
    }
    dvec2 gap_phase=phase(kw*gap);
    for(int row=0;row<samples;++row) {
        int base=row*128;
        for(int p=0;p<128;++p) put(base+p,0u);
        put(base,0x49334e52u);put(base+1,1u);put(base+2,uint(row));
        put(base+4,uint(nonce));put(base+5,uint(nonce)^0xffffffffu);
        put(base+8,8u);put(base+9,3u);put(base+10,uint(samples));
        double amplitudes[8];for(int p=0;p<8;++p) amplitudes[p]=0.0LF;
        double norm2=ref*ref;
        for(int f=0;f<4;++f) {
            double lo=scalar(scaler,f),hi=scalar(scaler,4+f);
            double value=(scalar(features,row*4+f)-lo)/(hi-lo);
            int channel=(f<2)?f:f+2;
            amplitudes[channel]=value;norm2+=value*value;
        }
        amplitudes[6]=ref;
        if(!(norm2>0.0LF)) { put(base+3,2u);continue; }
        double norm=sqrt(norm2),input_power=0.0LF;
        number(base+12,norm2);number(base+14,norm);
        for(int p=0;p<8;++p) { amplitudes[p]/=norm;number(base+70+2*p,amplitudes[p]);input_power+=amplitudes[p]*amplitudes[p]; }
        dvec2 ax[16],ay[16],out_field[8];
        for(int p=0;p<16;++p) { ax[p]=dvec2(0.0LF);ay[p]=dvec2(0.0LF); }
        for(int p=0;p<8;++p) out_field[p]=dvec2(0.0LF);
        for(int j=0;j<4;++j) ax[j]=amplitudes[j]*gap_phase;
        for(int i=0;i<4;++i) ay[i*4]=amplitudes[4+i]*gap_phase;
        int cells_done=0;
        for(int i=0;i<4;++i) for(int j=0;j<4;++j) {
            ++cells_done;
            int cell=i*4+j;
            double displacement=scalar(theta,cell)*wavelength/(4.0LF*PI);
            dvec2 first=-multiply(bs*(ax[cell]+times_i(ay[cell])),phase(kw*(5.0LF+2.0LF*displacement)));
            dvec2 second=-multiply(bs*(times_i(ax[cell])+ay[cell]),phase(kw*3.0LF));
            dvec2 ox=bs*(times_i(first)+second),oy=bs*(first+times_i(second));
            if(i+1<4) ax[(i+1)*4+j]+=multiply(ox,phase(kw*(X[i+1]-X[i]-1.0LF)));
            else out_field[j]=multiply(ox,gap_phase);
            if(j+1<4) ay[i*4+j+1]+=multiply(oy,phase(kw*(Y[j+1]-Y[j]-2.0LF)));
            else out_field[4+i]=multiply(oy,gap_phase);
        }
        double total=0.0LF,best=-1.0LF;int predicted=0;
        for(int p=0;p<8;++p) {
            number(base+16+4*p,out_field[p].x);number(base+18+4*p,out_field[p].y);
            double power=out_field[p].x*out_field[p].x+out_field[p].y*out_field[p].y;
            number(base+48+2*p,power);total+=power;
            if(p<3) { number(base+64+2*p,gain*power);if(power>best) { best=power;predicted=p; } }
        }
        number(base+86,input_power);number(base+88,total);
        put(base+6,uint(predicted));put(base+7,uint(cells_done));put(base+3,1u);put(base+11,1u);
    }
}
