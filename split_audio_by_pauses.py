from __future__ import annotations
import parselmouth
from parselmouth.praat import call
import tgt

def find_silence(file_path):
    silencedb = -25 
    minpause = 1.2     
    try:
        sound = parselmouth.Sound(file_path)
        
        originaldur = sound.duration
        intensity = sound.to_intensity(50)

        min_intensity = call(intensity, "Get minimum", 0, 0, "Parabolic")
        max_intensity = call(intensity, "Get maximum", 0, 0, "Parabolic")
        print('Maximum intensity: ', max_intensity)

        # get .99 quantile to get maximum (without influence of non-speech sound bursts)
        max_99_intensity = call(intensity, "Get quantile", 0, 0, 0.99)
        print('99 quantile for intensity: ', max_99_intensity)

        # estimate Intensity threshold
        threshold = max_99_intensity + silencedb
        threshold2 = max_intensity - max_99_intensity
        threshold3 = silencedb - threshold2
        if threshold < min_intensity:
            threshold = min_intensity
        print('Threshold = ', threshold3)

--------------------------------------------------------------------------
# textgrid object: 

# SilenceThreshold (threshold3) determines the maximum silence intensity value in dB (calculated max_intensdity - silenceThreshold); 
# intervals with an intensity smaller than this value are considered as silent intervals.

# Minimum silent interval (s) determines the minimum duration for an interval to be considered as silent. 

# Silent interval label determines the label for a silent interval in the TextGrid.

# Sounding interval label determines the label for a sounding interval in the TextGrid.

--------------------------------------------------------------------------
        # get pauses (silences) and speakingtime
        textgrid = call(
            intensity,
            "To TextGrid (silences)",
            threshold3,
            minpause,
            0.1,
            "silent",
            "sounding",
        )

        call(textgrid, 'Save as text file', '/Users/path_to_save_textgrid')

        silencetier = call(textgrid, "Extract tier", 1)
        silencetable = call(silencetier, "Down to TableOfReal", "sounding")
        npauses = call(silencetable, "Get number of rows")

        speakingtot = 0

        for ipause in range(npauses):
            pause = ipause + 1
            beginsound = call(silencetable, "Get value", pause, 1)
            endsound = call(silencetable, "Get value", pause, 2)
            speakingdur = endsound - beginsound
            speakingtot += speakingdur

        npause = npauses - 1

        return {
            "Number of Pauses": npause,
            "Duratrion": originaldur
        }


    except Exception as e:
        return {
            "Number of Pauses": str(e),
            "Duratrion": str(e)
        }

print(find_silence('/Users/audio_file_path/'))

tg = tgt.read_textgrid('/Users/path_to_textgrid_saved_above')
print('Reading textgrid')

print('Tier names', tg.get_tier_names())

silent_sounding_tier = tg.get_tier_by_name('silences')

silent_sounding_tier.annotations

sounding_tier = silent_sounding_tier.get_annotations_with_text('sounding')
print('Sounding tier ', sounding_tier)

sounding_parts_list = []
for interval in sounding_tier:
  start = interval.start_time
  end = interval.end_time
  sounding_parts_list.append((start, end))
print('Sounding parts ', sounding_parts_list)

sound = parselmouth.Sound('/Users/audio_file_path/')

i = 1
for values in sounding_parts_list:
  start = values[0]
  end = values[1]
  part = sound.extract_part(from_time=start, to_time=end)
  part.save('/Users/saving_directory_' + 'audio_8_' + str(i) + '.wav', 'WAV')
  print('Saving audio number' + str(i))
  i += 1


