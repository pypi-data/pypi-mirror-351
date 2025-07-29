def initialize_model():
    DEGREE = 2
    SMOOTHING = int(input('Enter smoothing amount (see README): '))

    import matplotlib.pyplot as plot
    import numpy

    from scipy.interpolate import UnivariateSpline

    from ExoRM import get_exorm_filepath, ExoRM, unique_radius, read_rm_data, preprocess_data, ForecasterRM

    data = read_rm_data()
    data = unique_radius(data)
    data = preprocess_data(data)

    x = data['radius']
    y = data['mass']

    x = numpy.log10(x)
    y = numpy.log10(y)

    model = UnivariateSpline(x, y, k = DEGREE, s = SMOOTHING)
    model = ExoRM(model, x, y)

    x_smooth = numpy.linspace(-0.5, 2, 10000)
    y_smooth = model(x_smooth)

    min_crossing = x_smooth[numpy.argmin(numpy.abs(y_smooth - ForecasterRM.terran(x_smooth)))]
    max_crossing = x_smooth[numpy.argmin(numpy.abs(y_smooth - ForecasterRM.stellar(x_smooth)))]

    model.override_min(min_crossing, model(min_crossing))
    model.override_max(max_crossing, model(max_crossing))

    y_smooth = model(x_smooth)

    plot.scatter(x, y, s = 0.3)
    plot.plot(x_smooth, y_smooth)
    plot.show()

    model.save(get_exorm_filepath('radius_mass_model.pkl'))