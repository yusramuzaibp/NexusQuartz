# =======================================================================
# INPUT RANGE VALIDATION
# Ranges are grounded in the actual public datasets each model was
# trained on, not guessed. Values outside these ranges are almost
# certainly typos (e.g. an extra digit) rather than real patients, and
# also fall outside what the model ever saw during training -- so a
# prediction on them is unreliable even if it "runs" without error.
#
# Sources:
#   Diabetes    -> Pima Indians Diabetes Dataset
#   Heart       -> UCI Cleveland Heart Disease Dataset
#   Parkinson's -> UCI Oxford Parkinson's Disease voice dataset
#
# Each entry: field_name -> (min, max, human label, short reason)
# =======================================================================

DIABETES_RANGES = {
    'Pregnancies':              (0,     17,     'Pregnancies',
                                  'training data max is 17'),
    'Glucose':                  (40,    250,    'Plasma Glucose (2h OGTT)',
                                  'typical range is 70-200 mg/dL'),
    'BloodPressure':            (30,    130,    'Diastolic Blood Pressure',
                                  'normal diastolic is roughly 60-90 mmHg'),
    'SkinThickness':            (0,     100,    'Triceps Skin Fold Thickness',
                                  'training data max is ~99mm'),
    'Insulin':                  (0,     900,    '2-Hour Serum Insulin',
                                  'training data max is ~846 µU/mL'),
    'BMI':                      (10,    70,     'Body Mass Index (BMI)',
                                  'training data max is ~67; real-world BMI virtually never exceeds 90-100'),
    'DiabetesPedigreeFunction': (0.0,   2.5,    'Diabetes Pedigree Function',
                                  'training data ranges ~0.08-2.42'),
    'Age':                      (1,     120,    'Age',
                                  'training data ranges 21-81, widened for any real age'),
}

HEART_RANGES = {
    'age':      (18,   100,  'Age',
                 'Cleveland dataset ranges 29-77'),
    'sex':      (0,    1,    'Sex',
                 'must be 0 (female) or 1 (male)'),
    'cp':       (0,    3,    'Chest Pain Type',
                 'valid categories are 0-3'),
    'trestbps': (70,   220,  'Resting Blood Pressure',
                 'Cleveland dataset ranges 94-200 mmHg'),
    'chol':     (100,  600,  'Serum Cholesterol',
                 'Cleveland dataset ranges 126-564 mg/dL'),
    'fbs':      (0,    1,    'Fasting Blood Sugar flag',
                 'must be 0 or 1'),
    'restecg':  (0,    2,    'Resting ECG Results',
                 'valid categories are 0-2'),
    'thalach':  (60,   220,  'Maximum Heart Rate Achieved',
                 'Cleveland dataset ranges ~71-202 bpm'),
    'exang':    (0,    1,    'Exercise Induced Angina flag',
                 'must be 0 or 1'),
    'oldpeak':  (0.0,  7.0,  'ST Depression (Exercise)',
                 'Cleveland dataset ranges 0-6.2'),
    'slope':    (0,    2,    'Slope of Peak Exercise ST',
                 'valid categories are 0-2'),
    'ca':       (0,    4,    'Major Vessels Colored (Fluoroscopy)',
                 'valid values are 0-4'),
    'thal':     (0,    3,    'Thalassemia',
                 'valid categories are 0-3'),
}

# Parkinson's voice features -- these are not intuitive, so the range
# alone won't mean much to a user, but it will catch decimal-point/typo
# errors (e.g. entering 15.0 instead of 0.015 for a jitter measure).
PARKINSONS_RANGES = {
    'fo':             (60,      300,     'MDVP:Fo(Hz)',       'avg vocal fundamental frequency, dataset ranges ~88-260 Hz'),
    'fhi':            (80,      650,     'MDVP:Fhi(Hz)',      'max vocal fundamental frequency, dataset ranges ~102-592 Hz'),
    'flo':            (50,      250,     'MDVP:Flo(Hz)',      'min vocal fundamental frequency, dataset ranges ~65-239 Hz'),
    'jitter_pct':     (0.0,     0.05,    'MDVP:Jitter(%)',    'dataset ranges ~0.0017-0.033'),
    'jitter_abs':     (0.0,     0.0005,  'MDVP:Jitter(Abs)',  'dataset ranges ~0.000007-0.00026'),
    'rap':            (0.0,     0.03,    'MDVP:RAP',          'dataset ranges ~0.0007-0.021'),
    'ppq':            (0.0,     0.03,    'MDVP:PPQ',          'dataset ranges ~0.0009-0.02'),
    'ddp':            (0.0,     0.09,    'Jitter:DDP',        'dataset ranges ~0.002-0.064'),
    'shimmer':        (0.0,     0.2,     'MDVP:Shimmer',      'dataset ranges ~0.01-0.12'),
    'shimmer_db':     (0.0,     2.0,     'MDVP:Shimmer(dB)',  'dataset ranges ~0.09-1.3'),
    'apq3':           (0.0,     0.1,     'Shimmer:APQ3',      'dataset ranges ~0.005-0.056'),
    'apq5':           (0.0,     0.12,    'Shimmer:APQ5',      'dataset ranges ~0.006-0.079'),
    'apq':            (0.0,     0.2,     'MDVP:APQ',          'dataset ranges ~0.007-0.138'),
    'dda':            (0.0,     0.3,     'Shimmer:DDA',       'dataset ranges ~0.014-0.169'),
    'nhr':            (0.0,     0.6,     'NHR',               'dataset ranges ~0.0007-0.315'),
    'hnr':            (0.0,     40.0,    'HNR',               'dataset ranges ~8.4-33.0'),
    'rpde':           (0.0,     1.0,     'RPDE',              'bounded complexity measure, dataset ranges ~0.26-0.69'),
    'dfa':            (0.4,     1.0,     'DFA',               'dataset ranges ~0.57-0.83'),
    'spread1':        (-10.0,   0.0,     'spread1',           'dataset ranges ~ -7.96 to -2.43 (always negative)'),
    'spread2':        (0.0,     0.6,     'spread2',           'dataset ranges ~0.006-0.45'),
    'd2':             (1.0,     4.5,     'D2',                'dataset ranges ~1.42-3.67'),
    'ppe':            (0.0,     0.7,     'PPE',               'dataset ranges ~0.045-0.53'),
}


def validate_ranges(values: dict, rules: dict):
    """
    values: dict of field_name -> raw value (already confirmed non-empty
            and successfully converted to float by the caller)
    rules:  one of DIABETES_RANGES / HEART_RANGES / PARKINSONS_RANGES

    Returns a list of human-readable warning strings, one per field that
    falls outside its known-good range. Empty list = everything looks
    plausible.
    """
    warnings = []
    for field, value in values.items():
        if field not in rules:
            continue
        min_val, max_val, label, reason = rules[field]
        if value < min_val or value > max_val:
            warnings.append(
                f"**{label}** = {value} looks out of range "
                f"(expected {min_val}-{max_val}; {reason}). "
                f"Double-check this value -- an extra or missing digit "
                f"is a common cause."
            )
    return warnings
