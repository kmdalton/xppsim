import argparse
import numpy as np
import pandas as pd

argDict = {
    "Fon"                      : "CNS file containing pumped structure factor amplitudes.",
    "Foff"                     : "CNS file containing un-pumped structure factor amplitudes.",
    "out"                      : "CSV intensity file to output.", 
    "--multiplicity"           : "Multiplicity of the dataset. Default is 10.",
    "--missing"                : "Fraction of missing reflections.",
    "--intensityshape"         : "Shape parameter for the distribution of intensities",
    "--intensityloc"           : "Location parameter for the distribution of intensities",
    "--intensityslope"         : "Relation between intensity metadata and reflection intensities",
    "--intensityoffset"        : "Intercept of the intensity measurements",
    "--reflectionsperimage"    : "Average number of reflections per image (default 150)",
    "--reflectionsperimagestd" : "Std deviation of reflectiosn per image (default 50)",
    "--minreflectionsperimage" : "Minimum reflections to generate per image",
    "--minimages"              : "Minimum images per run/crystal",
    "--meannimages"            : "Mean images per run/crystal",
    "--stdimages"              : "Standard deviation images per run/crystal",
    "--onreps"                 : "Number of on images per phi angle.",
    "--offreps"                : "Number of off images per phi angle.",
    "--sigintercept"           : "Sigma(I) = m*I + b. b",
    "--sigslope"               : "Sigma(I) = m*I + b. m",
    "--partialitymean"         : "Average partiality of reflections",
    "--partialitystd"          : "Average partiality of reflections",
    "--partialitymin"          : "Minimum partiality of reflections",
    "--sigInoise"              : "Fractional error. SigI=error*I + u",
    "--runlength"              : "Approximate number of phi angles per crystal",

    #Beam geometry parameters
    "--sigx"                   : "Variance in x pos in 'microns'",
    "--sigy"                   : "Variance in y pos in 'microns'",
    "--divx"                   : "Beam x divergence in 'microns'",
    "--divy"                   : "Beam y divergence in 'microns'",

    #Crystal dimensions and alignment parameters
    "--sigheight"              : "Variance of crystal dimension in microns",
    "--sigwidth"               : "Variance of crystal dimension in microns",
    "--height"                 : "Mean of crystal dimension in microns",
    "--width"                  : "Mean of crystal dimension in microns",
    "--sigalign"               : "Variance of crystal alignment dimension in microns",
}

datatypes = {
    "--multiplicity"           : float ,
    "--missing"                : float , 
    "--intensityshape"         : float ,
    "--intensityloc"           : float , 
    "--intensityslope"         : float ,
    "--intensityoffset"        : float ,
    "--reflectionsperimage"    : int,
    "--reflectionsperimagestd" : int,
    "--minreflectionsperimage" : int,
    "--minimages"              : int,
    "--meannimages"            : int,
    "--stdimages"              : int, 
    "--onreps"                 : int,
    "--offreps"                : int,
    "--sigintercept"           : float,
    "--sigslope"               : float, 
    "--partialitymean"         : float,
    "--partialitystd"          : float,
    "--partialitymin"          : float,
    "--sigInoise"              : float,
    "--runlength"              : int,

    #Beam geometry parameters
    "--sigx"                   : float,
    "--sigy"                   : float,
    "--divx"                   : float,
    "--divy"                   : float,

    #Crystal dimensions and alignment parameters
    "--sigheight"              : float,
    "--sigwidth"               : float,
    "--height"                 : float,
    "--width"                  : float,
    "--sigalign"               : float,
}

defaults = {
    "--multiplicity"           : 10.,
    "--missing"                : 0.0, 
    "--intensityshape"         : 2.,
    "--intensityloc"           : 0.2, 
    "--intensityslope"         : 1.0,
    "--intensityoffset"        : 0.0,
    "--reflectionsperimage"    : 150,
    "--reflectionsperimagestd" : 50,
    "--minreflectionsperimage" : 50,
    "--minimages"              : 10,
    "--meannimages"            : 10,
    "--stdimages"              : 10, 
    "--onreps"                 : 4, 
    "--offreps"                : 4,
    "--sigintercept"           : 5.,
    "--sigslope"               : 0.03, 
    "--partialitymean"         : 0.6,
    "--partialitystd"          : 0.2, 
    "--partialitymin"          : 0.1, 
    "--sigInoise"              : 0.03,
    "--runlength"              : 50, 

    #Beam geometry parameters
    "--sigx"                   : 10.,
    "--sigy"                   : 5.,
    "--divx"                   : 50.,
    "--divy"                   : 100.,

    #Crystal dimensions and alignment parameters
    "--sigheight"              : 10.,
    "--sigwidth"               : 10.,
    "--height"                 : 100.,
    "--width"                  : 100.,
    "--sigalign"               : 10.,
}

def parsehkl(inFN):
    F = pd.read_csv(inFN, 
        delim_whitespace=True, 
        names=['H','K','L','F'],
        usecols=[1,2,3,5], 
        skiprows=4,
        index_col=['H','K','L']
    )
    return F


def build_model(offFN, onFN, **kw):
    Fon,Foff = parsehkl(onFN),parsehkl(offFN)
    Foff['gamma'] = np.square(Fon['F']/Foff['F'])
    model = Foff.sample(frac=kw.get('multiplicity', 10.), replace=True)
    model['Foff'] = model['F']
    model['Fon'] = Fon.loc[model.index]
    del model['F']

    #you could do this with np.repeat in a couple of lines but it is unreadable
    minref  = kw.get('minreflections', 50)
    meanref = kw.get('reflectionsperimage', 150)
    stdref  = kw.get('reflectionsperimagestd', 50)
    nrefs = int(np.random.normal(meanref, stdref))
    nrefs = max(nrefs, minref)
    imagenumber = [0]*nrefs

    while len(imagenumber) < len(model):
        nrefs = int(np.random.normal(meanref, stdref))
        nrefs = max(nrefs, minref)
        imagenumber += [imagenumber[-1] + 1]*nrefs
        #Stop criterion
        if len(imagenumber) > len(model):
            imagenumber = imagenumber[:len(model)]
        
    model["IMAGENUMBER"] = imagenumber

    meanimages = kw.get('meanimages', 50)
    stdimages = kw.get('stdimages', 20)
    minimages = kw.get('minimages', 10)
    runs = []
    images = list(model['IMAGENUMBER'].unique())
    while len(images) > 0:
        ct = max(minimages, int(np.random.normal(meanimages, stdimages)))
        if len(images) < ct:
            ct = len(images)
        runs.append([images.pop(0) for i in range(ct)])

    #Crystal orientation
    sigalign = kw.get("sigalign", 10.)

    #Crystal dimensions 
    height = kw.get("height", 50.)
    width  = kw.get("width", 100.)
    sigh   = kw.get("sigheight", 10.)
    sigw   = kw.get("sigwidth", 10.)

    model['RUN'] = 0
    for n,run in enumerate(runs, 1):
        x = np.random.normal(0., sigalign)
        y = np.random.normal(0., sigalign)
        h = np.random.normal(height, sigh)
        w = np.random.normal(width , sigw)
        model.loc[model['IMAGENUMBER'].isin(run), 'RUN'] = n
        model.loc[model['IMAGENUMBER'].isin(run), 'CRYSTBOTTOM'] = y - h/2.
        model.loc[model['IMAGENUMBER'].isin(run), 'CRYSTTOP']    = y + h/2.
        model.loc[model['IMAGENUMBER'].isin(run), 'CRYSTLEFT']   = x - w/2.
        model.loc[model['IMAGENUMBER'].isin(run), 'CRYSTRIGHT']  = x + w/2.

    partiality = np.random.normal(kw.get("partialitymean", 0.6), kw.get("partialitystd", 0.2), len(model))
    partiality = np.minimum(partiality, 1.)
    partiality = np.maximum(partiality, kw.get("partialitymin", 0.1))
    model['P'] = partiality
    I = None
    sigx,sigy = kw.get('sigx', 10.),kw.get('sigy', 5.)

    pd.concat((model

    model['SERIES'] = 'off1'
    for i in range(kw.get('offreps', 4)-1):
        m = model.copy()
        m['SERIES'] = 'off{}'.format(i+2)
        model = pd.concat((model, m))

    for i in range(kw.get('onreps', 4)):
        m = model.copy()
        m['SERIES'] = 'on{}'.format(i+1)
        model = pd.concat((model, m))

    model['BEAMX'],model['BEAMY'],model['Io'] = 0.,0.,0.
    model['BEAMX'] = model.groupby(['RUN', 'IMAGENUMBER', 'SERIES']).transform(lambda x: np.random.normal(0., sigx))
    model['BEAMY'] = model.groupby(['RUN', 'IMAGENUMBER', 'SERIES']).transform(lambda x: np.random.normal(0., sigy))
    model['Io'] = model.groupby(['RUN', 'IMAGENUMBER', 'SERIES']).transform(lambda x: np.random.normal(0., sigy))
         np.random.gamma(kw.get('intensityloc', 0.2), kw.get('intensityshape', 2.0), len(iobs))
#TODO: Finish populating this using the above tranform syntax
    #what do we still need?
#Io,IPM
    return model.sample(frac = 1. - kw.get('missing', 0.), replace=False)

"""
    for i in range(kw.get("onreps", 4)):
        
        iobs = model.copy()
        model.loc[model['IMAGENUMBER'].isin(run), 'BEAMX'] = np.random.normal(0, sigx)
        model.loc[model['IMAGENUMBER'].isin(run), 'BEAMY'] = np.random.normal(0, sigy)
        iobs['intensity'] = np.random.gamma(kw.get('intensityloc', 0.2), kw.get('intensityshape', 2.0), len(iobs))
        iobs['SERIES'] = 'on{}'.format(i + 1)
        iobs['IOBS'] = model['P']*iobs['intensity']*model['Fon']**2
        iobs['SIGMA(IOBS)'] = kw.get("sigintercept", 5.0) + kw.get("sigslope", 0.03)*iobs['IOBS']
        iobs['IOBS'] = [np.random.normal(i, j) for i,j in zip(iobs['IOBS'], iobs['SIGMA(IOBS)'])]
        I = pd.concat((I, iobs))

    for i in range(kw.get("offreps", 4)):
        iobs = model.copy()
        iobs['intensity'] = np.random.gamma(kw.get('intensityloc', 0.2), kw.get('intensityshape', 2.0), len(iobs))
        iobs['SERIES'] = 'off{}'.format(i + 1)
        iobs['IOBS'] = model['P']*iobs['intensity']*model['Fon']**2
        iobs['SIGMA(IOBS)'] = kw.get("sigintercept", 5.0) + kw.get("sigslope", 0.03)*iobs['IOBS']
        iobs['IOBS'] = [np.random.normal(i, j) for i,j in zip(iobs['IOBS'], iobs['SIGMA(IOBS)'])]
        I = pd.concat((I, iobs))
"""
    return I.sample(frac = 1. - kw.get('missing', 0.), replace=False)



def main():
    parser = argparse.ArgumentParser()
    for k,v in argDict.items():
        parser.add_argument(k, help=v, default=defaults.get(k, None), type=datatypes.get(k, None))

    #TODO: parser.add_argument("--signal_decay", default=None, help="Exponential decay constant to model how I/sig(I) decays with resolution. Default is 0 (no decay).")

    parser = parser.parse_args()
    model  = build_model(parser.Fon, parser.Foff, **vars(parser))
    model.to_csv(parser.out)


if __name__=="__main__":
    main()
