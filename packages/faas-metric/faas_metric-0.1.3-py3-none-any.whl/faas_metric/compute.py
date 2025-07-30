import pandas as pd

def compute_faas(wer_list, speaker_metadata):
    """
    Compute the FAAS (Fairness Adjusted ASR Score).

    Parameters:
        wer_list (list of float): List of WERs for different utterances.
        speaker_metadata (list of dict): Metadata per speaker including fairness-related attributes.

    Returns:
        float: The computed FAAS score.
    """
    if not wer_list:
        raise ValueError("WER list cannot be empty")

    avg_wer = sum(wer_list) / len(wer_list)
    faas = 100 - avg_wer  # Dummy logic
    return faas
