# Flashcards Prototype: AI-Powered Language Learning

This project is a command-line interface (CLI) application that helps you learn new words in a foreign language by focusing on understanding their meaning in context, rather than just memorizing translations. It uses AI to generate dynamic flashcards that adapt to your learning progress.

## The Problem with Traditional Flashcards

Traditional flashcards often rely on rote memorization of translations. This can be an inefficient way to learn a language, as it doesn't teach you how to use words in different situations. You might know the translation of a word, but you might not be able to use it correctly in a sentence.

## Our Approach: Learning Through Inference

This flashcard app takes a different approach. Instead of just showing you the translation of a word, it provides you with multiple example sentences that use the word in different contexts. This helps you to infer the meaning of the word and understand how it's used in different situations.

## How It Works

The app uses a spaced-repetition algorithm to show you flashcards at the optimal time for learning. It also uses AI to generate new example sentences for each word, so you're always learning something new.

The app has two practice modes:

*   **Multiple-Choice "Blitz":** This mode helps you to quickly learn the meaning of new words.
*   **Typing "Mastery":** This mode helps you to practice using words in sentences.

## Getting Started

To get started, you'll need to import a list of words that you want to learn. The app accepts a tab-separated file (`.tsv`) with the following format:

```
translation	context_sentence_with_[[target]]
```

For example:

```
assumido	Peter has [[taken up]] his English with great reluctance.
```

Once you've imported your words, you can start practicing!

## The Goal

The goal of this project is to create a more effective and engaging way to learn a new language. By focusing on understanding words in context, we hope to help you to become a more confident and fluent speaker.
