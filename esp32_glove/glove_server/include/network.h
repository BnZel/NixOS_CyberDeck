#ifndef NETWORK_H
#define NETWORK_H

#define PORT         1234
#define BUFFER_SIZE  4096
#define NUM_CLIENTS  2

struct glove
{
    // identifier
    char name[16];

    // potentiometers
    long A2,A3,A4,D32,D33;

    // mpu9250 accelerometer 
    float x,y,z;
};

struct servo
{
    // servos
    long s1,s2,s3,s4;
};

void parseData(struct glove *glove_, struct servo *servo_, char buffer[]);
void sendData(int clientSocket, struct glove *glove, struct servo *servo);
void *manageClient(void *args);
void startServer();

#endif
