import json



def correct_prodigy_dataset(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    corrected_data = []
    for line in lines:
        example = json.loads(line)
        
        # if example.get("answer") == "reject":
        #     continue
        
        if "spans" in example and example["spans"]:
            # filtrer les spans incomplets
            corrected_spans = []
            for span in example["spans"]:
                if all(key in span for key in ["text", "start", "end", "label"]):
                    # supprimer les sauts de ligne et les espaces au début et à la fin du texte du span
                    span["text"] = span["text"].strip()
                    # ajuster les positions start et end 
                    span_start = example["text"].find(span["text"])
                    if span_start != -1: 
                        span["start"] = span_start
                        span["end"] = span_start + len(span["text"])
                        corrected_spans.append(span)
            example["spans"] = corrected_spans
        else:
            continue
        corrected_data.append(example)

    with open(output_file, "w", encoding="utf-8") as f:
        for example in corrected_data:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"Correction terminée. Fichier corrigé enregistré sous : {output_file}")

input_file = "/home/lexia/works/RevolutionAI/Core/Libs-python/src/data/annotations_manual.jsonl"
output_file = "/home/lexia/works/RevolutionAI/Core/Libs-python/src/data/annotations__manual_correct_NoReject.jsonl"
correct_prodigy_dataset(input_file,output_file)