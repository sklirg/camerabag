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


def _safe_get(d, key, default=''):
    return d.get(key, default)
