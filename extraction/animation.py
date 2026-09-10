class AnimationExtractor:
    def extract(self, stage):
        from contexts import AnimationStatistics

        animation = AnimationStatistics()

        for prim in stage.TraverseAll():
            for attribute in prim.GetAttributes():
                if not attribute.ValueMightBeTimeVarying():
                    continue

                time_samples = attribute.GetTimeSamples()

                if not time_samples:
                    continue

                invalid_samples = self._find_invalid_time_samples(
                    attribute,
                    time_samples,
                )

                animation.invalid_time_samples.extend(
                    invalid_samples
                )

        return animation

    @staticmethod
    def _find_invalid_time_samples(attribute, time_samples):
        invalid_samples = []

        previous_time = None

        for time in time_samples:
            if previous_time is not None and time <= previous_time:
                invalid_samples.append({
                    "attribute": attribute.GetPath().pathString,
                    "time": time,
                    "previous_time": previous_time,
                })

            previous_time = time

        return invalid_samples