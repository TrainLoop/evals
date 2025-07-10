# 🤖📊 TrainLoop Evals

TrainLoop Evals is a comprehensive LLM evaluation framework designed for developers who need simple, vendor-independent evaluation tools.

## Core Principles

- **Simplicity First** – One environment variable, one function call, one folder of JSON files
- **Vendor Independence** – Everything stored as newline-delimited JSON; no databases required  
- **Type-Safe & Extensible** – In-code tests with full TypeScript support and composable system
- **Meet Developers Where They Are** – Works with existing workflows and bespoke loops

<p align="center">
  <img src="images/drake_evals.png" alt="Evals Meme" width="400" height="auto" />
</p>

## Quick Start

```bash
# Install the CLI
pipx install trainloop-cli

# Create a workspace
trainloop init

# Set your data path
export TRAINLOOP_DATA_FOLDER=/path/to/data

# Run evaluations
trainloop eval

# View results
trainloop studio
```

## 📚 Documentation

For comprehensive documentation, installation guides, tutorials, and API reference:

**👉 [evals.docs.trainloop.ai](https://evals.docs.trainloop.ai)**

### Quick Links
- **[Getting Started](https://evals.docs.trainloop.ai/getting-started/installation)** - Installation and setup
- **[Quick Start Guide](https://evals.docs.trainloop.ai/getting-started/quick-start)** - Complete walkthrough
- **[SDK Guides](https://evals.docs.trainloop.ai/guides)** - Python, TypeScript, and Go integration
- **[CLI Reference](https://evals.docs.trainloop.ai/reference)** - Complete command documentation
- **[Contributing](https://evals.docs.trainloop.ai/development/contributing)** - Development setup and guidelines

## Demo

- **Demo Repository**: [chat-ui-demo](https://github.com/TrainLoop/chat-ui-demo)
- **Live Demo**: [evals.trainloop.ai](https://evals.trainloop.ai)

## Support

- **[GitHub Issues](https://github.com/trainloop/evals/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/trainloop/evals/discussions)** - Community support and questions
- **[Documentation](https://evals.docs.trainloop.ai)** - Comprehensive guides and tutorials

## License

[License information would go here]

---

**Need help?** Check out our [comprehensive documentation](https://evals.docs.trainloop.ai) or [open an issue](https://github.com/trainloop/evals/issues).