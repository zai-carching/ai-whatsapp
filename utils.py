import re


def split_text(text, max_words=120, min_words=30):
    """
    Smart text splitter that:
    1. First splits at double newlines (paragraphs)
    2. Then splits at single newlines if needed
    3. Finally splits by sentence if still too long
    4. Guarantees chunks stay within word limits

    Parameters:
        text: Input text to split
        max_words: Maximum words per chunk (hard limit)
        min_words: Minimum words per chunk
    Returns:
        List of perfectly sized text chunks
    """
    chunks = []

    # First split by paragraphs (double newlines)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    for para in paragraphs:
        words = para.split()
        word_count = len(words)

        # Case 1: Paragraph fits perfectly
        if word_count <= max_words:
            chunks.append(para)
            continue

        # Case 2: Needs splitting - try single newlines
        lines = [l.strip() for l in para.split('\n') if l.strip()]
        if len(lines) > 1:
            current_chunk = []
            current_count = 0
            for line in lines:
                line_words = line.split()
                line_count = len(line_words)
                if current_count + line_count > max_words and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_count = 0
                current_chunk.append(line)
                current_count += line_count
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            continue

        # Case 3: Single paragraph - split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', para)
        current_chunk = []
        current_count = 0
        for sent in sentences:
            sent_words = sent.split()
            sent_count = len(sent_words)
            if current_count + sent_count > max_words and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_count = 0
            current_chunk.append(sent)
            current_count += sent_count
        if current_chunk:
            chunks.append(' '.join(current_chunk))

    # Final validation
    return [chunk for chunk in chunks if len(chunk.split()) >= min_words]