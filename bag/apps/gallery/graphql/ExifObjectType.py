import graphene


class ExifNode(graphene.ObjectType):
    aperture = graphene.NonNull(graphene.String)
    camera_model = graphene.NonNull(graphene.String)
    exposure_program = graphene.NonNull(graphene.String)
    f_stop = graphene.NonNull(graphene.Float)
    focal_length = graphene.NonNull(graphene.String)
    lens_model = graphene.NonNull(graphene.String)
    iso = graphene.NonNull(graphene.String)
    shutter_speed = graphene.NonNull(graphene.String)
    coordinates = graphene.NonNull(graphene.List(graphene.NonNull(graphene.Float)))

    def resolve_aperture(self, info):
        return _safe_get(self, 'EXIF FNumber')

    def resolve_camera_model(self, info):
        return _safe_get(self, 'Image Model')

    def resolve_exposure_program(self, info):
        return _safe_get(self, 'EXIF ExposureProgram')

    def resolve_f_stop(self, info):
        fnumber = _safe_get(self, 'EXIF FNumber')
        if not fnumber:
            return 0

        if fnumber.isnumeric():
            return float(fnumber)

        if "/" not in fnumber:
            return 0

        a = fnumber.split("/")[0]
        b = fnumber.split("/")[1]

        if not (a.isnumeric() and b.isnumeric()):
            return 0

        return float(a) / float(b)

    def resolve_iso(self, info):
        return _safe_get(self, 'EXIF ISOSpeedRatings')

    def resolve_lens_model(self, info):
        return _safe_get(self, 'EXIF LensModel')

    def resolve_shutter_speed(self, info):
        return _safe_get(self, 'EXIF ExposureTime')

    def resolve_focal_length(self, info):
        return _safe_get(self, 'EXIF FocalLength')

    def resolve_coordinates(self, info):
        raw_latitude = _safe_get(self, 'GPS GPSLatitude')
        raw_longitude = _safe_get(self, 'GPS GPSLongitude')

        longitude_ref = _safe_get(self, 'GPS GPSLongitudeRef')  # West/East
        latitude_ref = _safe_get(self, 'GPS GPSLatitudeRef')  # North/South

        if not raw_latitude and not raw_longitude:
            return []

        latitude = convert_exif_coord_to_coord(raw_latitude)
        longitude = convert_exif_coord_to_coord(raw_longitude)

        return [
            latitude if latitude_ref == 'N' else -latitude,
            longitude if longitude_ref == 'E' else -longitude,
        ]


def _safe_get(d, key, default=''):
    return d.get(key, default)

def convert_exif_coord_to_coord(coordinate):
    deg, minutes, seconds = coordinate[1:len(coordinate) - 1].split(',')

    deg = float(deg)

    if '/' in minutes:
        minutes = float(int(minutes.split('/')[0]) / int(minutes.split('/')[1]))
    else:
        minutes = float(minutes)

    seconds = float(seconds)

    return deg + minutes / 60 + seconds / 3600
