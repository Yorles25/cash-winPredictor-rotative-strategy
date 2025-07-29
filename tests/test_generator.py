from src.generator import generate_predictions

def test_generate_predictions():
    preds = generate_predictions("strategy_config.json")
    assert isinstance(preds, list)
    assert all(isinstance(n, int) for n in preds)
