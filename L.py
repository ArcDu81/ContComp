import random
import string

def generate_complex_document(filename="complex_test_file.txt", target_words=100000):
    entities = {
        "people": ["Dr. Aris Thorne", "Elena Rostova", "Marcus Vance", "Dr. Chen Wei", "Silas Vance"],
        "companies": ["Nexus Dynamics", "Aetherion Labs", "Vanguard Cybernetics", "Quantum Core Tech"],
        "projects": ["Project HYDRA", "Titan Initiative", "Neural-Weave", "Aegis Protocol"],
        "locations": ["Neo-Tokyo", "Geneva Facility", "Sector 4", "The Archon Base"]
    }

    # Core relationships we want the LLM to successfully extract and merge
    core_plot_points = [
        "Dr. Aris Thorne secretly transferred the Aegis Protocol schematics from Nexus Dynamics to Aetherion Labs.",
        "Elena Rostova is the lead engineer for Project HYDRA but reports covertly to Marcus Vance.",
        "Quantum Core Tech funded the Geneva Facility construction to mask the development of the Titan Initiative.",
        "Silas Vance, brother of Marcus Vance, was exiled from Vanguard Cybernetics after the Sector 4 incident."
    ]

    filler_vocabulary = [
        "analyzed", "synthesized", "integrated", "deployed", "operational", "clandestine", 
        "encrypted", "bandwidth", "neural", "latency", "framework", "architecture", "protocol",
        "the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on",
        "are", "as", "with", "his", "they", "I", "at", "be", "this", "have", "from", "or", "one",
        "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can",
        "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if", "will"
    ]

    print(f"Generating complex document with ~{target_words} words...")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# CONFIDENTIAL: GLOBAL INTELLIGENCE REPORT 2026\n\n")
        
        word_count = 10
        paragraph_count = 0
        
        while word_count < target_words:
            paragraph = []
            
            # Every 50 paragraphs, insert a crucial cross-dependent plot point
            if paragraph_count % 50 == 0 and paragraph_count > 0:
                plot_point = random.choice(core_plot_points)
                paragraph.append(f"CRITICAL INTEL: {plot_point}")
                word_count += len(plot_point.split())
            
            # Generate random complex-sounding filler text referencing entities
            for _ in range(random.randint(50, 150)):
                if random.random() < 0.05:  # 5% chance to insert an entity
                    category = random.choice(list(entities.keys()))
                    entity = random.choice(entities[category])
                    paragraph.append(entity)
                    word_count += len(entity.split())
                else:
                    word = random.choice(filler_vocabulary)
                    paragraph.append(word)
                    word_count += 1
                    
            f.write(" ".join(paragraph) + ".\n\n")
            paragraph_count += 1

    print(f"Success! Generated '{filename}' with {word_count} words.")

if __name__ == "__main__":
    generate_complex_document()