#ifndef POINT_CC
#define POINT_CC

#include<cmath>

struct Point
{
    double X;
    double Y;
    double Z;
    
    Point Scale(double rhs)
    {
        auto ret = Point(0,0,0);
        ret.X = (*this).X * rhs;
        ret.Y = (*this).Y * rhs;
        ret.Z = (*this).Z * rhs;
        return ret;    
    }
    Point operator+(Point rhs)
    {
        auto ret = Point(0,0,0);
        ret.X = (*this).X + rhs.X;
        ret.Y = (*this).Y + rhs.Y;
        ret.Z = (*this).Z + rhs.Z;
        return ret;
    }
    
    Point(double xx,double yy,double zz)
    {
        X = xx;
        Y = yy;
        Z = zz;
    }
    Point()
    {
        X=0;
        Y=0;
        Z=0;
    }
};

#endif
