import numpy

from math import sin,cos,pi

def rotate(xangle1,yangle2,zangle3):
    #creates rotation matrix for rotation by xangle1 around x-axis,
    #followed by rotation by yangle2 around y-axis,
    #followed by rotation by zangle3 around z-axis,
    #see: https://en.wikipedia.org/wiki/Rotation_matrix
    angle1=xangle1*pi/180
    angle2=yangle2*pi/180
    angle3=zangle3*pi/180
    #rotate around x-axis by 10°

    Rx=numpy.array([[1,0,0],[0,cos(angle1),-sin(angle1)],[0,sin(angle1),cos(angle1)]])

    #rotate around y-axis by 30°

    Ry=numpy.array([[cos(angle2),0,sin(angle2)],[0,1,0],[-sin(angle2),0,cos(angle2)]])

    #rotate around z-axis by 60°

    Rz=numpy.array([[cos(angle3),-sin(angle3),0],[sin(angle3),cos(angle3),0],[0,0,1]])

    Rxy=numpy.matmul(Ry,Rx)
    Rxyz=numpy.matmul(Rz,Rxy)
    return Rxyz
