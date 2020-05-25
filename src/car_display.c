#include "mpu9250.h"
#include <stdio.h>

int main(){
    __u16 test[3];
    int ret;

    init_mpu(0);
    // init_therm();
    while(1){
        //ret = get_temp();
        //printf("%d\n", ret);
        ret = read_accel_raw(test);
        printf("%d    %d, %d, %d\n", ret, test[0], test[1], test[2]);
        sleep(1);
    }
    return 0;
}