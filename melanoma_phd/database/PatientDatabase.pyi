# Stub file for annotating PatientDatabase dynamic properties created during execution time for being displayed in the linter.
# IMPORTANT: A new dynamic property has to be added here in order to being displayed by linter.
from melanoma_phd.database.DatabaseSheet import DatabaseSheet

class PatientDatabase:
    general_clinical_database: DatabaseSheet = None
    blood_parameters_database: DatabaseSheet = None
    lf_dna_populations_database: DatabaseSheet = None
    radiological_tests_database: DatabaseSheet = None
    ap_ampliation_database: DatabaseSheet = None
