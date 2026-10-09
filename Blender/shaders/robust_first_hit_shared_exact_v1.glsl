// Fixed integer ABI and exact rules, one invocation and no CPU geometry.
uint diagnostic_stage=0u,diagnostic_triangle=0xffffffffu;
uint input_word(uint i){return input_packet.words[i>>2u][int(i&3u)];}
ivec2 texel(uint i){return ivec2(int(i&63u),int(i>>6u));}
void put(uint i,uint value){imageStore(result_words,texel(i),uvec4(value,0u,0u,0u));}
void put512(uint offset,int r){for(int i=0;i<16;++i)put(offset+uint(i),reg512[r][i]);}
bool load_scalar(uint sid,int r) {
    if(sid>=input_word(4u)||input_word(6u)!=8u)return false;
    uint base=input_word(5u)+sid*8u;
    return decode_hilo(uvec2(input_word(base),input_word(base+1u)),r);
}
bool load_source(uint sid) {
    if(sid>=input_word(7u)||input_word(9u)!=32u)return false;
    uint base=input_word(8u)+sid*32u;
    if(input_word(base)!=sid||input_word(base+1u)!=0xffffffffu)return false;
    for(int i=0;i<6;++i)if(!load_scalar(input_word(base+2u+uint(i)),i))return false;
    return !zero3(3);
}
bool load_vertex(uint vid,int r) {
    if(vid>=input_word(10u)||input_word(12u)!=8u)return false;
    uint base=input_word(11u)+vid*8u;
    if(input_word(base)!=vid)return false;
    for(int i=0;i<3;++i)if(!load_scalar(input_word(base+3u+uint(i)),r+i))return false;
    return true;
}
// Classes: outside0, interior1, boundary2, contact3, coplanar4, degenerate5, numeric6.
int candidate(uint tri,out uint object_id) {
    uint base=input_word(14u)+tri*8u;
    object_id=input_word(base+1u);
    if(input_word(15u)!=8u||input_word(base)!=tri)return 6;
    for(int i=0;i<3;++i)if(!load_vertex(input_word(base+3u+uint(i)),6+3*i)){
        diagnostic_stage=10u;return 6;
    }
    if(!sub3(9,6,15)||!sub3(12,6,18)||!cross3(15,18,21)){diagnostic_stage=11u;return 6;}
    if(zero3(21))return 5;
    if(!cross3(3,18,24)||!dot3(15,24,33)||!sub3(0,6,27)){diagnostic_stage=12u;return 6;}
    if(zero512(33)) {
        if(!dot3(27,21,36))return 6;
        return zero512(36)?4:0;
    }
    if(!cross3(27,15,30)||!dot3(27,24,34)||!dot3(3,30,35)||!dot3(18,30,36)){
        diagnostic_stage=13u;return 6;
    }
    if(neg512(33))for(int r=33;r<=36;++r)negate512(r,r);
    if(!add512(34,35,37)){diagnostic_stage=14u;return 6;}
    if(neg512(36)||neg512(34)||neg512(35)||compare512(37,33)>0)return 0;
    if(zero512(36))return 3;
    if(zero512(34)||zero512(35)||compare512(37,33)==0)return 2;
    return 1;
}
void mask(uint tri,inout uint lo,inout uint hi) {
    if(tri<32u)lo|=1u<<tri;else hi|=1u<<(tri-32u);
}
void main() {
    if(any(notEqual(gl_GlobalInvocationID,uvec3(0u))))return;
    for(int r=0;r<64;++r)clear512(r);
    for(uint i=0u;i<uint(input_word_count);++i)
        imageStore(echo_words,texel(i),uvec4(input_word(i),0u,0u,0u));
    for(uint i=0u;i<64u;++i)put(i,0u);
    uint selected=0xffffffffu,selected_object=0xffffffffu,ties=0u,tlo=0u,thi=0u;
    uint contacts=0u,clo=0u,chi=0u,coplanars=0u,degenerates=0u,excluded=0u;
    bool best=false,boundary=false,ambiguous=false,numeric=false;
    bool header_ok=input_word_count>=32&&input_word(0u)==0x4e33484cu&&
        input_word(1u)==1u&&input_word(2u)==32u&&input_word(3u)==uint(input_word_count)&&
        input_word(13u)>0u&&input_word(13u)<=64u&&source_index>=0&&uint(source_index)<input_word(7u);
    if(!header_ok||!load_source(uint(source_index))) {numeric=true;diagnostic_stage=1u;}
    else for(uint tri=0u;tri<input_word(13u);++tri) {
        uint object_id;int klass=candidate(tri,object_id);
        if(klass==6){numeric=true;diagnostic_triangle=tri;break;}
        if(klass==5){degenerates++;continue;}
        if(klass==4){coplanars++;continue;}
        if(klass==3) {
            if(previous_primitive>=0&&uint(previous_primitive)==tri&&departure_event>=1&&departure_event<=3)excluded++;
            else{contacts++;mask(tri,clo,chi);}continue;
        }
        if(klass!=1&&klass!=2)continue;
        bool ok=true;int relation=best?compare_fraction(36,33,38,39,ok):-1;
        if(!ok){numeric=true;diagnostic_stage=20u;diagnostic_triangle=tri;break;}
        if(!best||relation<0) {
            best=true;copy512(36,38);copy512(33,39);
            for(int i=0;i<3;++i)copy512(21+i,40+i);
            selected=tri;selected_object=object_id;boundary=klass==2;
            ties=1u;tlo=0u;thi=0u;ambiguous=false;mask(tri,tlo,thi);
        } else if(relation==0) {
            ties++;mask(tri,tlo,thi);bool same=false;
            if(object_id==selected_object)same=parallel3(21,40,ok);
            if(!ok){numeric=true;diagnostic_stage=21u;diagnostic_triangle=tri;break;}
            if(!same)ambiguous=true;
        }
    }
    bool equivalent=ties>1u&&!ambiguous;
    uint status=numeric?8u:degenerates>0u?7u:coplanars>0u?6u:contacts>0u?5u:
        !best?2u:ambiguous?3u:boundary&&!equivalent?4u:1u;
    if(status!=1u&&status!=3u&&status!=4u) {
        selected=0xffffffffu;selected_object=0xffffffffu;clear512(38);clear512(39);
        ties=status==5u?contacts:0u;tlo=status==5u?clo:0u;thi=status==5u?chi:0u;
        equivalent=false;ambiguous=false;
    }
    put(0u,0x35484652u);put(1u,1u);put(2u,status);put(3u,uint(source_index));
    put(4u,selected);put(5u,selected_object);put(6u,ties);put(7u,uint(boundary));
    put(8u,excluded);put(9u,contacts);put(10u,coplanars);put(11u,degenerates);
    put(12u,input_word(13u));put(13u,uint(dispatch_nonce));put(14u,~uint(dispatch_nonce));put(15u,1u);
    put512(16u,38);put512(32u,39);put(48u,tlo);put(49u,thi);
    put(50u,uint(equivalent));put(51u,uint(ambiguous));
    put(52u,diagnostic_stage);put(53u,diagnostic_triangle);put(54u,arithmetic_failure);
}
