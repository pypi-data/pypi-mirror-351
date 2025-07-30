#ifndef GENERATOR_CC
#define GENERATOR_CC

//#if __has_include(<span>)
//    #include <span>
//#else
    #include "span.cc" // UGLY TEMPORARY HACK UNTIL YOUR CURRENT C++ COMPILER INCLUDES std::span SUPPORT
    namespace std {
        using tcb::span;
    }
//#endif

#include "Point.cc"
#include "Utils.cc"

#include <stdio.h>

namespace Generator
{
    bool CombineChains(std::span<Point> lhs, std::span<double> sizesLhs, std::span<Point> rhs, std::span<double> sizesRhs)
    {
        // We'll attempt to add beads from this chain to right chain one-by-one.
        double stepSize = sizesLhs.back() + sizesRhs[0];
        Point shift = lhs.back() + Utils::GetSpherical().Scale(stepSize); // Location of left end of right sub chain
        
        for(int i = 0; i < rhs.size() ; i++)
        {
            rhs[i] = rhs[i] + shift;
            for(int j = 0 ; j < lhs.size() ; j++)
            {
                if (i == 0 && j == lhs.size() -1) continue;
                double dist = Utils::SquaredDistance(lhs[j], rhs[i]);
                double minDist = sizesLhs[j] + sizesRhs[i];
                if(dist < minDist*minDist) return false;
            }
        }
        return true;
    }


    void GetChain(std::span<Point> ret, std::span<double> sizes, int recursionDepth = 0)
    {
        if(ret.size() == 1) // Chain is very small.
        {
            ret[0] = Point(0, 0, 0);
            return;
        }

        bool chainsAreCombined;
        int ml = ret.size() / 2;
        int mr = ret.size() - ml;
        do
        {
            GetChain(ret.first(ml), sizes.first(ml), recursionDepth + 1); // Get left sub chain
            GetChain(ret.last(mr), sizes.last(mr), recursionDepth + 1); // Get right sub chain
            chainsAreCombined = CombineChains(ret.first(ml), sizes.first(ml), ret.last(mr), sizes.last(mr));
        } while (!chainsAreCombined);
    }
    
    void GetChain(double *sizes,long unsigned int n,Point *locations)
    {
        // GetChain(double *sizes, long unsigned int n) -> Point*
        //
        // Generate chain of spheres forming self avoiding random walk (SARW) give sizes
        // Parameters
        // ----------
        // sizes : double*
        //   array of length `n` with sizes of beads
        // n : long unsigned int
        //   length of the sizes array
        // out : Point*
        //   return pointer to a size `n` array of Points
        
        //Point locations[n];
        std::span<Point> slocations{locations,n};
        std::span<double> ssizes{sizes,n};

        Generator::GetChain(slocations, ssizes);
                
        return;
    }
}

#endif /* GENERATOR_CC */
