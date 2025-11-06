#ifndef NETWORK_H
#define NETWORK_H

#define PORT         1234
#define BUFFER_SIZE  2048
#define NUM_CLIENTS  1

struct glove
{
    // potentiometers
    long A2,A3,A4,D32,D33;

    // mpu9250 accelerometer 
    float x,y,z;
};

void parseData(struct glove glove_, char buffer[]);
void *manageClient(void *args);
void startServer();

#endif
