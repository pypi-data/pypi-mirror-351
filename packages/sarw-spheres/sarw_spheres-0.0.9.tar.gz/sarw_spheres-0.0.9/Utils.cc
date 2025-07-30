#ifndef UTILS_CC
#define UTILS_CC

#include <random>

#include"Point.cc"


std::mt19937 generator(0);
std::uniform_real_distribution<> distribution(0.0, 1.0);

namespace Utils
{
    double FastSin(double x)
    {
        // Sin(\pi x) working on range [-1,1]
        double x2 = x*x;
        return x * (3.1415261777700003 + x2 * (-5.16637886247938 + x2 * (2.542630511490387 + x2 * (-0.5817495184869728 + x2 * 0.06397735352906153))));
    }

    double FastCos(double x)
    {
        // Cos(\pi x) working on range [-1,1]
        double x2 = x*x;
        return 1.0 + x2*(-4.934784351275681 + x2* (4.05835413719592 + x2*(-1.3332435316029887 + x2*(0.23064793981782827 - x2*0.020975729260541698))));
    }

    inline double GetUniform()
    {
        return distribution(generator);
        //return distribution(xorshf96);
    }

    Point GetSpherical()
    {
        double x = 2.0 * GetUniform() - 1.0;
        double phi = 2.0 * GetUniform() - 1.0;
        double scale = sqrt(1 - x * x);
        double y = scale * FastSin(phi); // double y = scale * sin(Math.PI*phi);
        double z = scale * FastCos(phi); // double z = scale * cos(Math.PI*phi);
        return Point(x, y, z);
    }

    double SquaredDistance(Point a, Point b)
    {
        return (a.X - b.X) * (a.X - b.X) + (a.Y - b.Y) * (a.Y - b.Y) + (a.Z - b.Z) * (a.Z - b.Z);
    }

    double Distance(Point a, Point b)
    {
        return sqrt(SquaredDistance(a, b));
    }
}

#endif
