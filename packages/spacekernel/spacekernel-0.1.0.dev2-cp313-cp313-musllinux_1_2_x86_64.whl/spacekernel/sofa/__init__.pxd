#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

cdef extern from "src/sofam.h" nogil:

    const double DPI # (3.141592653589793238462643)
    # Pi

    const double D2PI # (6.283185307179586476925287)
    # 2Pi

    const double DR2D # (57.29577951308232087679815)
    # Radians to degrees

    const double DD2R # (1.745329251994329576923691e-2)
    # Degrees to radians

    const double DR2AS # (206264.8062470963551564734)
    # Radians to arcseconds

    const double DAS2R # (4.848136811095359935899141e-6)
    # Arcseconds to radians

    const double DS2R # (7.272205216643039903848712e-5)
    # Seconds of time to radians

    const double TURNAS # (1296000.0)
    # Arcseconds in a full circle

    const double DMAS2R # (DAS2R / 1e3)
    # Milliarcseconds to radians

    const double DTY # (365.242198781)
    # Length of tropical year B1900 (days)

    const double DAYSEC # (86400.0)
    # Seconds per day.

    const double DJY # (365.25)
    # Days per Julian year

    const double DJC # (36525.0)
    # Days per Julian century

    const double DJM # (365250.0)
    # Days per Julian millennium

    const double DJ00 # (2451545.0)
    # Reference epoch (J2000.0), Julian Date

    const double DJM0 # (2400000.5)
    # Julian Date of Modified Julian Date zero

    const double DJM00 # (51544.5)
    # Reference epoch (J2000.0), Modified Julian Date

    const double DJM77 # (43144.0)
    # 1977 Jan 1.0 as MJD

    const double TTMTAI # (32.184)
    # TT minus TAI (s)

    const double DAU # (149597870.7e3)
    # Astronomical unit (m, IAU 2012)

    const double CMPS # 299792458.0
    # Speed of light (m/s)

    const double AULT # (DAU/CMPS)
    # Light time for 1 au (s)

    const double  DC # (DAYSEC/AULT)
    # Speed of light (au per day)

    const double ELG # (6.969290134e-10)
    # L_G = 1 - d(TT)/d(TCG)

    const double ELB # (1.550519768e-8)
    const double TDB0 # (-6.55e-5)
    # L_B = 1 - d(TDB)/d(TCB), and TDB (s) at TAI 1977/1/1.0

    const double SRS # 1.97412574336e-8
    # Schwarzschild radius of the Sun (au)
    # = 2 * 1.32712440041e20 / (2.99792458e8)^2 / 1.49597870700e11

    double dint(double A) # ((A)<0.0?ceil(A):floor(A))
    # dint(A) - truncate to nearest whole number towards zero (double)

    double dnint(double A) # (fabs(A)<0.5?0.0:((A)<0.0?ceil((A)-0.5):floor((A)+0.5)))
    # dnint(A) - round to nearest whole number (double)

    double dsign(double A, double B) # ((B)<0.0?-fabs(A):fabs(A))
    # dsign(A,B) - magnitude of A with sign of B (double)

    double gmax(double A, double B) # (((A)>(B))?(A):(B))
    # max(A,B) - larger (most +ve) of two numbers (generic)

    double gmin(double A, double B) # (((A)<(B))?(A):(B))
    # min(A,B) - smaller (least +ve) of two numbers (generic)

    const short WGS84  # 1
    const short GRS80  # 2
    const short WGS72  # 3
    # Reference ellipsoids

cdef extern from "src/sofa.h" nogil:

    # ---------- ---------- ---------- ---------- time and date functions
    int iauCal2jd(int iy, int im, int id, double *djm0, double *djm)
    void iauD2tf(int ndp, double days, char *sign, int ihmsf[4])
    int iauD2dtf(const char *scale, int ndp, double d1, double d2,
                 int *iy, int *im, int *id, int ihmsf[4])
    int iauDat(int iy, int im, int id, double fd, double *deltat)
    double iauDtdb(double date1, double date2,
                   double ut, double elong, double u, double v)
    int iauDtf2d(const char *scale, int iy, int im, int id,
                 int ihr, int imn, double sec, double *d1, double *d2)
    double iauEpb(double dj1, double dj2)
    void iauEpb2jd(double epb, double *djm0, double *djm)
    double iauEpj(double dj1, double dj2)
    void iauEpj2jd(double epj, double *djm0, double *djm)
    int iauJd2cal(double dj1, double dj2,
                  int *iy, int *im, int *id, double *fd)
    int iauJdcalf(int ndp, double dj1, double dj2, int iymdf[4])
    int iauTaitt(double tai1, double tai2, double *tt1, double *tt2)
    int iauTaiut1(double tai1, double tai2, double dta,
                  double *ut11, double *ut12)
    int iauTaiutc(double tai1, double tai2, double *utc1, double *utc2)
    int iauTcbtdb(double tcb1, double tcb2, double *tdb1, double *tdb2)
    int iauTcgtt(double tcg1, double tcg2, double *tt1, double *tt2)
    int iauTdbtcb(double tdb1, double tdb2, double *tcb1, double *tcb2)
    int iauTdbtt(double tdb1, double tdb2, double dtr,
                 double *tt1, double *tt2)
    int iauTf2d(char s, int ihour, int imin, double sec, double *days)
    int iauTttai(double tt1, double tt2, double *tai1, double *tai2)
    int iauTttcg(double tt1, double tt2, double *tcg1, double *tcg2)
    int iauTttdb(double tt1, double tt2, double dtr,
                 double *tdb1, double *tdb2)
    int iauTtut1(double tt1, double tt2, double dt,
                 double *ut11, double *ut12)
    int iauUt1tai(double ut11, double ut12, double dta,
                  double *tai1, double *tai2)
    int iauUt1tt(double ut11, double ut12, double dt,
                 double *tt1, double *tt2)
    int iauUt1utc(double ut11, double ut12, double dut1,
                  double *utc1, double *utc2)
    int iauUtctai(double utc1, double utc2, double *tai1, double *tai2)
    int iauUtcut1(double utc1, double utc2, double dut1,
                  double *ut11, double *ut12)

    # ---------- ---------- ---------- ---------- vector and matrix
    void iauTrxp(double r[3][3], double p[3], double trp[3])
    void iauTr(double r[3][3], double rt[3][3])
    void iauCr(double r[3][3], double c[3][3])
    void iauRx(double phi, double r[3][3])
    void iauRy(double theta, double r[3][3])
    void iauRz(double psi, double r[3][3])
    void iauRxr(double a[3][3], double b[3][3], double atb[3][3])
    void iauRxp(double r[3][3], double p[3], double rp[3])
    void iauIr(double r[3][3])

    # ---------- ---------- ---------- ---------- earth attitude
    void iauXys00a(double date1, double date2, double *x, double *y, double *s)
    void iauC2ixys(double x, double y, double s, double rc2i[3][3])
    double iauEra00(double dj1, double dj2)
    double iauGmst82(double dj1, double dj2)
    double iauSp00(double date1, double date2)
    void iauPom00(double xp, double yp, double sp, double rpom[3][3])

    # ---------- ---------- ---------- ---------- misc
    void iauMoon98(double date1, double date2, double pv[2][3])
    int iauPlan94(double date1, double date2, int np, double pv[2][3])
    double iauAnp(double a)
    int iauEpv00(double date1, double date2, double pvh[2][3], double pvb[2][3])
    void iauAb(double pnat[3], double v[3], double s, double bm1, double ppr[3])
    int iauEform(int n, double *a, double *f)