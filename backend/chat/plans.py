from enum import Enum


class DataType(Enum):
    species_occurrence_records = ["occurrence_records", "species_occurrence_records"]
    species_occurrence_record_statistics = ["occurrence_record_statistics", "occurrence_record_counts",
                                            "occurrence_records_summary"]
    species_occurrence_record_collections = ["occurrence_record_collections", "occurrence_record_sets"]
    species_media_records = ["specimen_media_records", "specimen_image_records"]
    species_media = ["specimen_media", "specimen_images"]
    species_occurrence_map = ["occurrence_records_map", "species_occurrence_map"]
    species_occurrence_records_download_email = ["species_occurrence_records_download_email",
                                                 "occurrence_records_download_email"]
