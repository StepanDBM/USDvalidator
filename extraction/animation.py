from contexts import AnimatedPropertyInfo, AnimationStatistics, ValueClipInfo


class AnimationExtractor:
    def extract(self, stage):
        animation = AnimationStatistics()
        for prim in stage.TraverseAll():
            animation.value_clips.extend(self._clips(prim))
            for attribute in prim.GetAttributes():
                time_samples = attribute.GetTimeSamples()
                if not time_samples:
                    continue
                animation.time_sample_count += len(time_samples)
                animation.properties.append(AnimatedPropertyInfo(
                    attribute.GetPath().pathString,
                    tuple(float(value) for value in time_samples),
                    bool(attribute.ValueMightBeTimeVarying()),
                ))
                animation.invalid_time_samples.extend(
                    self._find_invalid_time_samples(attribute, time_samples)
                )
        return animation

    @staticmethod
    def _clips(prim):
        result = []
        for name, values in (prim.GetMetadata("clips") or {}).items():
            result.append(ValueClipInfo(
                prim.GetPath().pathString,
                str(name),
                tuple(str(item.path if hasattr(item, "path") else item) for item in values.get("assetPaths", ())),
                str(values.get("primPath", "")),
                str(getattr(values.get("manifestAssetPath"), "path", values.get("manifestAssetPath", "")) or ""),
                tuple(tuple(item) for item in values.get("active", ())),
                tuple(tuple(item) for item in values.get("times", ())),
                str(getattr(values.get("templateAssetPath"), "path", values.get("templateAssetPath", "")) or ""),
            ))
        return result

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
