precision mediump float;
uniform sampler2D texture;
uniform int max_vertex_deg;
uniform int node_count;
uniform float k_2;
uniform float k;
uniform float gravity;
uniform float speed;
uniform float max_displace;
uniform int tex_width;
uniform int tex_height;
varying vec2 vTextureCoord;


//indice start from 1
ivec2 indiceToCoords(int indice) {
    int indice0 = indice - 1;
    int x = int(mod(float(indice0), float(tex_width))) + 1;
    int y = indice0 / tex_width + 1;
    return ivec2(x, y);
}

int coordsToIndice(int x, int y) {
    return (y-1)*tex_width+x;
}

void main() {
    const int MAX_ITERATIONS = 999999;
    float dx=0.0, dy=0.0;
    int i_x = int(floor(vTextureCoord.s*float(tex_width)+0.5));
    int i_y = int(floor(vTextureCoord.t*float(tex_height)+0.5));
    // vec4 node_i = texture2D(texture, vTextureCoord);
    vec4 node_i = texture2D(texture, vec2(
            (float(i_x-1)+0.5)/float(tex_width),
            (float(i_y-1)+0.5)/float(tex_height) ));
    gl_FragColor = node_i;
    if(coordsToIndice(i_x, i_y)>node_count) {return;}
    //repulsive force
    for(int j=1; j<MAX_ITERATIONS; j++) {
        if(j > node_count) {break;}
        ivec2 coords = indiceToCoords(j);
        int j_x = coords.x;
        int j_y = coords.y;
        if(i_x!=j_x && i_y!=j_y) {
            vec4 node_j = texture2D(texture, vec2(
                (float(j_x-1)+0.5)/float(tex_width),
                (float(j_y-1)+0.5)/float(tex_height) ));
            float x_dist = node_i.r - node_j.r;
            float y_dist = node_i.g - node_j.g;
            float dist = sqrt(x_dist*x_dist + y_dist*y_dist);
            if(dist > 0.0) {
                // float repl_f = k_2 / dist;
                float repl_f = 0.00004*float(node_i.a)*float(node_j.a)/dist;
                dx += x_dist / dist * repl_f;
                dy += y_dist / dist * repl_f;
            }
        }
    }
    //attractive force
    int offset_indice = int(floor(node_i.b + 0.5));
    int len = int(floor(node_i.a + 0.5));
    vec4 node_buffer;
    for(int p=0; p<MAX_ITERATIONS; p++) {
        if(p >= len || p > max_vertex_deg) {break;}
        int arr_idx = offset_indice + p;
        int buf_offset = arr_idx - arr_idx / 4 * 4;
        if(p==0 || buf_offset==0) {
            ivec2 offset_coords = indiceToCoords((arr_idx)/4+1);
            int offset_x = offset_coords.x;
            int offset_y = offset_coords.y;
            node_buffer = texture2D(texture, vec2(
                (float(offset_x-1)+0.5)/float(tex_width),
                (float(offset_y-1)+0.5)/float(tex_height) ));
        }
        float float_j = buf_offset == 0 ? node_buffer.r :
                        buf_offset == 1 ? node_buffer.g :
                        buf_offset == 2 ? node_buffer.b :
                                          node_buffer.a;
        ivec2 target = indiceToCoords(int(float_j)+1);
        int target_x = target.x;
        int target_y = target.y;
        vec4 node_j = texture2D(texture, vec2(
                (float(target_x-1)+0.5)/float(tex_width),
                (float(target_y-1)+0.5)/float(tex_height) ));
        float x_dist = node_i.r - node_j.r;
        float y_dist = node_i.g - node_j.g;
        float dist = sqrt(x_dist*x_dist + y_dist*y_dist);
        // float attr_f = dist * dist / k;
        float attr_f = log(1.0+dist);
        if(dist > 0.0) {
            dx -= x_dist / dist * attr_f;
            dy -= y_dist / dist * attr_f;
        }
    }
    //gravity
    float d = sqrt(node_i.r*node_i.r + node_i.g*node_i.g);
    // float gf = 0.01 * k * gravity * d;
    float gf = gravity*(node_i.a+1.0);
    dx -= gf * node_i.r / d;
    dy -= gf * node_i.g / d;
    //speed
    dx *= speed;
    dy *= speed;
    float dist = sqrt(dx*dx + dy*dy);
    if(dist > 0.0) {
        float limited_dist = min(max_displace*speed, dist);
        gl_FragColor.r += dx / dist * limited_dist;
        gl_FragColor.g += dy / dist * limited_dist;
    }
}
