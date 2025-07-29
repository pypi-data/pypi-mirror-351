# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.
# `chATLAS_Embed/VectorStoreCreators.py`

"""A collection of different VectorStoreCreators.

IMPLEMENTATIONS HERE:
TWikiHTMLVectorStoreCreator - Creates a Twiki vectorstore from HTML Files
TWikiTextVectorStoreCreator - Creates a Twiki vectorstore from TEXT Files

CDSTextVectorStoreCreator - Creates CDS vectorstore from CDS TEXT files

ATLASTalkVectorStoreCreator - Creates ATLAS Talk vectorstore from ATLAS talk json in eos
"""
import urllib.parse

import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import as_completed
from collections import Counter
import textwrap


from chATLAS_Embed.TwikiProcessors import *
from chATLAS_Embed.Base import *
from tqdm import tqdm
import json
import os
import re
from datetime import datetime, timedelta
import requests
import time
import random
import math


# ---- VECTORSTORE FROM HTML TWIKI DOCUMENTS ----
class TWikiHTMLVectorStoreCreator(BaseVectorStoreCreator):
    """VectorStore creator for Twiki documents from HTML files."""

    def process_document(self, html_content: str) -> Document:
        """Process a document from string into standard Document format.

        :param html_content: (str) - string of preprocessed HTML content

        :return:
        Document of HTML data
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract TWiki metadata
        title = soup.find("title").text if soup.find("title") else ""
        url = (
            soup.find("link", rel="canonical")["href"]
            if soup.find("link", rel="canonical")
            else ""
        )

        # Process page_content
        content = self._extract_content(soup)

        return Document(
            page_content=content,
            metadata={"title": title, "url": url, "type": "twiki"},
            id=self._generate_id(url),
        )

    def load_documents(self, input_path: Path) -> List[str]:
        """Load HTML documents from directory in `input_path`

        :param input_path: (Path) - Path to directory containing HTML files
        """
        html_files = []
        for file_path in input_path.glob("**/*.html"):
            with open(file_path, "r", encoding="utf-8") as f:
                html_files.append(f.read())
        return html_files

    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        # Extract and clean page_content
        main_content = soup.find("div", {"class": "twikiMain"})
        if main_content:
            # Remove unwanted elements
            for element in main_content.find_all(["script", "style"]):
                element.decompose()
            return main_content.get_text(separator=" ", strip=True)
        return ""

    @staticmethod
    def _generate_id(url: str) -> str:
        return url.split("/")[-1]


# ---- VECTORSTORE FROM TEXT TWIKI DOCUMENTS ----
class TWikiTextVectorStoreCreator(BaseVectorStoreCreator):
    """Vector store creator for TWiki text files."""

    def process_document(self, twiki_doc: TWikiTextDocument) -> Document:
        """
        Process TWiki text document into Document format.
        :param twiki_doc: (TWikiTextDocument) - Preprocessed text file into TwikiTextDocument format

        :return:
        Document containing text content
        """
        return Document(
            page_content=twiki_doc.content,
            metadata={
                "type": "twiki",
                "name": twiki_doc.name,
                "url": twiki_doc.url,
                "parent_structure": twiki_doc.parent_structure,
                "last_modification": twiki_doc.last_modification,
                "html_file_path": twiki_doc.html_path,
            },
            id=twiki_doc.name,
        )

    def load_documents(self, input_path: Path) -> List[TWikiTextDocument]:
        """Load TWiki documents from text files contained in directory
        `input_path`.

        :param input_path: (Path) - Path to directory containing .txt files
        """
        processor = TWikiTextProcessor()
        documents = []

        for file_path in tqdm(input_path.glob("**/*.txt")):
            if file_path.stem == "processed":
                continue
            try:
                doc = processor.read_twiki_text(file_path)
                documents.append(doc)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return documents


class CDSTextVectorStoreCreator(BaseVectorStoreCreator):
    """Class to load and process CDS docs into standard document form to be
    added to DB."""

    def load_documents(self, input_path: Path) -> List[Any]:
        """Load CDS docs from path into Document form Currently set up to use
        CDS docs in `/eos/atlas/atlascerngroupdisk/phys-
        mlf/Chatlas/Database/Scraping/CDS` but should theoretically work
        wherever the docs are stored as latex.txt files and with meta_info.txt
        files."""
        # Initialize a list to store the file paths

        documents = []
        for file_path in input_path.rglob("latex.txt"):
            # Get metadata
            with open(file_path.parent / "meta_info.txt", "r", encoding="utf-8") as f:
                try:
                    for line in f:
                        if line.startswith("PAPER NAME :"):
                            paperName = line.split(":", 1)[1].strip()
                        elif line.startswith("LAST MODIFICATION DATE :"):
                            lastModification = line.split(":", 1)[1].strip()
                            date_str = lastModification
                            try:
                                # Try parsing as yyyy-mm-dd first
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                try:
                                    # Try parsing as dd-mm-yyyy
                                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                                except ValueError:
                                    # If neither format works, use current date
                                    date_obj = datetime.now()
                            lastModification = date_obj.strftime("%d-%m-%Y")
                        elif line.startswith("URL :"):
                            url = line.split(":", 1)[1].strip()
                except Exception as e:
                    print(f"Error processing document {file_path.parent} - Error: {e}")
                    continue
            # Get CDS doc page_content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            doc = Document(
                page_content=content,
                metadata={
                    "type": "CDS",
                    "name": paperName,
                    "url": url,
                    "last_modification": lastModification,
                },
                id=paperName,
            )
            documents.append(doc)

        return documents

    def process_document(self, document: Any) -> Document:
        """Already in Document dataclass format on input so can just return."""
        return document


class IndicoTranscriptsVectorStoreCreator(BaseVectorStoreCreator):
    """Class to load and process Indico transcripts into standard document form to be
    added to DB."""

    def load_documents(self, input_path: Path) -> List[Any]:
        """Load Indico transcripts from path into Document form."""
        # Initialize a list to store the file paths

        documents = []
        for file_path in input_path.rglob("*.json"):
            # Get metadata
            with open(file_path, "r") as f:
                try:
                    json_data = json.load(f)
                    for category in json_data.keys():
                        events = json_data[category]
                        for url in events.keys():
                            date_str = events[url]["metadata"]["date"]
                            try:
                                # Try parsing as yyyy-mm-dd first
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                try:
                                    # Try parsing as dd-mm-yyyy
                                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                                except ValueError:
                                    # If neither format works, use current date
                                    date_obj = datetime.now()
                            date = date_obj.strftime("%d-%m-%Y")

                            content = events[url]["general"]
                            if content != "":
                                doc = Document(
                                    page_content=content,
                                    metadata={
                                        "type": "Indico",
                                        "name": category,
                                        "last_modification": date,
                                        "url": url,
                                        "category": file_path.name.split(".json")[0],
                                    },
                                    id=category,
                                )
                                documents.append(doc)
                            else:
                                contributions = events[url]["contributions"]
                                for contribution in contributions.keys():
                                    content = contributions[contribution]
                                    doc = Document(
                                        page_content=content,
                                        metadata={
                                            "type": "Indico",
                                            "name": contribution,
                                            "last_modification": date,
                                            "url": url,
                                            "category": file_path.name.split(".json")[
                                                0
                                            ],
                                        },
                                        id=category,
                                    )
                                    documents.append(doc)
                except Exception as e:
                    print(f"Error processing document {file_path.parent} - Error: {e}")
                    continue

        return documents

    def process_document(self, document: Any) -> Document:
        """Already in Document dataclass format on input so can just return."""
        return document


class syncedTwikiVectorStoreCreator(BaseVectorStoreCreator):
    """
    Designed to load documents from the ATLAS Twiki rsync space
    """

    def __init__(
        self,
        vector_store: VectorStore,
        child_splitter: TextSplitter,
        parent_splitter: TextSplitter,
        output_dir: Path,
    ):
        """
        Designed to load documents from the ATLAS Twiki rsync space

        :param VectorStore vector_store: Instantiated VectorStore to add documents to
        :param TextSplitter child_splitter: Child splitter to use to split parent documents into child chunks
        :param TextSplitter parent_splitter: Parent splitter to split documents into chunks
        :param Path output_dir: Directory for creation of csv file tracking modifications and storage

        Current metadata is:
        - 'last_modification': last modification of twiki in format (%d-%m-%Y) (dd-mm-YYYY)
        - 'date': full date including seconds of last modification of twiki (not really needed)
        - 'name': name of the twiki
        - 'type': "twiki" - ie it is type twiki
        - 'url': url to the twiki
        - 'author': who wrote twiki
        - 'format': twiki format (irrelevant and could be removed as only 2 options
        - 'version': twiki version number
        - 'category': [str] - list of found catagories this document is part of
        - 'topic_parent': name of parent twiki based on
        - 'parent_index': generated automatically - index of parent in db
        - 'search_type': generated automatically - 'embedding' | 'text'
        """
        super().__init__(vector_store, child_splitter, parent_splitter, output_dir)
        self.skipped_docs = []
        self.kept_docs = []

    def process_document(self, document: Any) -> Document:
        return document

    def load_documents(self, input_path: Path) -> List[Any]:
        """
        Load documents from input path of type from twiki dump using parallel processing
        :param input_path: Path to overall twiki dump
        :type input_path: Path
        :return: List of loaded documents
        :rtype: List[Document]
        """
        # Get list of all text files first
        txt_files = []
        input_depth = len(input_path.parts)
        for root, _, files in os.walk(input_path):
            current_depth = len(Path(root).parts)
            if (
                current_depth - input_depth <= 1
            ):  # Only process if within 1 level deep from input
                for file in files:
                    if file.endswith(".txt"):
                        txt_files.append(Path(os.path.join(root, file)))
        docs_returned = []

        # Use ThreadPoolExecutor for parallel processing
        # Number of workers = min(32, os.cpu_count() * 4) is a good default
        max_workers = min(32, os.cpu_count() * 4) if os.cpu_count() else 4

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(self.process_single_document, file_path): file_path
                for file_path in txt_files
            }

            # Create progress bar with total number of files
            with tqdm(total=len(txt_files), desc="Processing files") as pbar:
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    try:
                        document = future.result()
                        if document:
                            docs_returned.append(document)
                    except Exception as e:
                        file_path = future_to_file[future]
                        print(f"Error processing file {file_path.stem}: {str(e)}")
                    pbar.update(1)

        if self.verbose:
            self.get_stats(docs_returned)

        return docs_returned

    def process_single_document(self, doc_path: Path) -> Document | None:
        """
        Process a single document into the correct form
        :param doc_path:
        :type doc_path:
        :return: Either processed document in correct form, or None if document couldn't be processed
        :rtype: Document | None
        """

        if not self.keep_by_name(doc_path.stem):
            skipped = {"name": doc_path.stem, "reason": "Excluded Name Pattern"}
            self.skipped_docs.append(skipped)
            return

        with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            parsed_content, metadata = self.extract_document(content, doc_path.stem)
            if not parsed_content or not metadata:
                skipped = {
                    "name": doc_path.stem,
                    "reason": "Not enough content or invalid metadata",
                }
                self.skipped_docs.append(skipped)
                return
            else:
                metadata["type"] = "twiki"
                metadata["name"] = doc_path.stem
                metadata["last_modification"] = metadata["date"].strftime(
                    "%d-%m-%Y"
                )  # Rework this into other form
                metadata["date"] = str(
                    metadata["date"]
                )  # put in json serializable form

                # Generate URL for this document
                base_dir = Path("/eos/user/c/chatwiki/ATLAS_TWiki")
                try:
                    trimmed_path = doc_path.relative_to(base_dir)
                except ValueError as e:
                    # Handling cases where you are running locally or a messed up file name
                    trimmed_path = doc_path
                url_path = trimmed_path.with_name(trimmed_path.stem)

                metadata["url"] = f"https://twiki.cern.ch/twiki/bin/view/{url_path}"

                self.kept_docs.append(doc_path)
                return Document(
                    page_content=parsed_content, metadata=metadata, id=doc_path.stem
                )

    @staticmethod
    def keep_by_name(doc_name: str) -> bool:
        """
        To keep the document based on its name or not
        :param doc_name: Document name
        :type doc_name: str
        :return: Is document of the right format and wanted to be kept?
        :rtype: bool
        """
        # Convert to lowercase once for case-insensitive comparisons
        doc_name_lower = doc_name.lower()

        # Exclusion sets for faster lookups
        releases_set = {
            "rel12",
            "rel13",
            "rel14",
            "rel15",
            "rel16",
            "rel17",
            "rel18",
            "r12",
            "r13",
            "r14",
            "r15",
            "r16",
            "r17",
            "r18",
            "release15",
            "release16",
            "mc08",
            "mc09",
            "mc10",
            "mc11",
            "mc12",
            "mc14",
            "mc15",
            "dc14",
        }

        years_set = {
            "run1",
            "ls1",
            "2009",
            "2010",
            "2011",
            "2012",
            "2013",
            "2014",
            "7tev",
            "8tev",
        }

        things_set = {
            "dpd",
            "d2pd",
            "d3pd",
            "minimumbias13",
            "hcw09",
            "hcw13",
            "hcw14",
            "hadroniccalibration1",
            "hadroniccalibrationworkshop09",
            "pasttaucpworkshops",
            "muonboydocumentation",
        }

        # Quick checks for specific conditions

        # Check for "172" but not "20172018"
        if "172" in doc_name and "20172018" not in doc_name:
            return False

        # Check for "mc13" but not "mc13tev"
        if "mc13" in doc_name_lower and "mc13tev" not in doc_name_lower:
            return False

        # Check for "Old" or "OLD" (but not within other words like "unfold")
        if any(x in doc_name for x in ("Old ", "OLD ", " Old", " OLD")):
            return False

        # Check against our sets
        if any(release in doc_name_lower for release in releases_set):
            return False

        if any(year in doc_name_lower for year in years_set):
            return False

        if any(thing in doc_name_lower for thing in things_set):
            return False

        # If none of the exclusion criteria matched, keep the document
        return True

    def extract_document(self, content: str, doc_name: str):
        """
        Extract document content and metadata from a document
        :param doc_name: name of the document
        :type doc_name: str
        :param content: document content in full
        :type content: str
        :return: content, metadata
        :rtype: (str, dict)
        """
        # -------- Check Document Not a Test Document
        if (
            re.search(r"---+\s*Just a Test Area", content)
            or re.search(r"%PDFALL%", content)
            or re.search(r"%PDFTHIS%", content)
        ):
            return None, None

        # --------- Extracting metadata ---------
        metadata_pattern = r"%META:TOPICINFO{(.*?)}%"
        parent_pattern = r"%META:TOPICPARENT{name=\"(.*?)\"}%"

        metadata_match = re.search(metadata_pattern, content)
        parent_match = re.search(parent_pattern, content)

        if not metadata_match:
            return None, None

        metadata_str = metadata_match.group(1)
        # Parse individual metadata fields
        metadata = {}
        for field in metadata_str.split():
            if "=" in field:
                key, value = field.split("=", 1)
                # Remove quotes if present
                metadata[key] = value.strip('"').lower()

        # Handle datetime from epoch
        try:
            metadata["date"] = datetime.fromtimestamp(int(metadata["date"]))
        except (ValueError, TypeError) as e:
            print(f"Date not found in document: {e}")
            return None, None

        metadata["topic_parent"] = parent_match.group(1) if parent_match else None

        metadata["category"] = self.categorize_parent_title(
            metadata["topic_parent"], doc_name
        )

        # --------- EXTRACT CONTENT ---------
        include_pattern = r"%STARTINCLUDE%(.*?)%STOPINCLUDE%"
        match = re.search(include_pattern, content, re.DOTALL)

        if not match:
            return None, None

        extracted_content = match.group(1)

        # Remove specified lines
        lines = extracted_content.split("\n")
        filtered_lines = [
            line
            for line in lines
            if not (
                line.strip().startswith("<!--")
                or line.strip().startswith("%RESPONSIBLE%")
                or line.strip().startswith("%REVIEW%")
            )
        ]

        # If twiki contains less than x lines, don't include it
        if len(filtered_lines) < 20:
            return None, None

        # Rejoin the filtered lines
        cleaned_content = "\n".join(filtered_lines)

        return cleaned_content, metadata

    def get_stats(self, docs_to_return):
        """
        Prints and logs some stats of the document loading process just to understand the data some more
        :param docs_to_return:
        :type docs_to_return:
        :return:
        :rtype:
        """
        skipped_files = list(set([doc["name"] for doc in self.skipped_docs]))
        print(
            f"Some example removed documents: {[doc_path for doc_path in skipped_files[:10]]}"
        )
        print(
            f"Total Number of documents kept: {len(docs_to_return)} / {len(set(self.kept_docs)) + len(skipped_files)}"
        )
        print(f"Total Number of documents skipped: {len(skipped_files)}")

        metadata_topic_parent = Counter()
        metadata_cat = Counter()
        metadata_last_modification = set()
        metadata_format = set()

        for doc in docs_to_return:
            metadata_topic_parent[doc.metadata["topic_parent"]] += 1
            for cat in doc.metadata["category"]:
                metadata_cat[cat] += 1
            metadata_last_modification.add(doc.metadata["last_modification"])
            metadata_format.add(doc.metadata["format"])

        # print(f"All topic parents: {metadata_topic_parent.most_common()}")
        print(f"Number of unique topic parents: {len(metadata_topic_parent)}")
        # print(f"All last modifications: {metadata_last_modification}")
        # print(f"Count last mod: {len(metadata_last_modification)}")
        # print(f"All metadata format: {metadata_format}")
        # print(f"Count metadata format: {len(metadata_format)}")
        print(f"All metadata cat: {metadata_cat}")
        print(f"Count metadata cat: {len(metadata_cat)}")

        # for doc in docs_to_return:
        #     if "misc" in doc.metadata["category"]:
        #         print(doc.metadata["topic_parent"], doc.metadata["name"])

    @staticmethod
    def categorize_parent_title(parent_title: str, title: str) -> []:
        """
        Categorise a title into a list of categories that can be found in the title
        :param parent_title: Title of parent document
        :type parent_title: str
        :param title: Title of actual document
        :type title: str
        :return: List of found categories
        :rtype: list
        """

        # Dictionary of patterns and their categories
        # Using tuples for patterns that should match the same category
        patterns = {
            "adc": "adc",
            "acts": "acts",
            "afs": "afs",
            "(?:ath|athena)": "athena",
            "atlfast": "atlfast",
            "(?:calo(?:rimeter)?s?)": "calorimeter",  # calo, calorimeter, calos, calorimeters
            "conditions?": "conditions",  # condition or conditions
            "cool": "cool",
            "database(?:s)?": "database",  # database or databases
            "(?:innerdetector|indet)": "innerdetector",
            "susy": "Susy",
            # Matches trigger, triggered, triggering, or the abbreviation trig variants
            "(?:trigger(?:ed|ing)?|trig(?:ger(?:ed|ing)?)?)": "trigger",
            "tdaq": "tdaq",
            "jet(?:s)?": "jet",  # jet or jets
            "jetetmiss": "jetetmiss",  # New distinct group
            "etmiss": "etmiss",  # New distinct group
            "higgs": "higgs",
            "dihiggs": "dihiggs",  # New addition
            "trt": "trt",
            "tgc": "tgc",
            # Matches tag, tagging, or tagged
            "tag(?:ging|ged)?": "tagging",
            "ama": "ama",
            "pixel(?:s)?": "pixel",
            "madgraph": "madgraph",
            "aod": "aod",
            "ami": "ami",
            # Matches track, tracking, tracker, or tracked
            "track(?:ing|er|ed)?": "tracking",
            "daq": "daq",
            "sensors?": "sensors",  # sensor or sensors
            "comput(?:e|ing|er)": "computing",  # compute, computing, or computer
            # Matches analysis or analyses
            "(?:analysis|analyses)": "analysis",
            "crc": "crc",
            "tools?": "tools",  # tool or tools
            # Matches reconstruct, reconstructing, reconstruction, or reconstructed
            "reconstruct(?:ing|ion|ed)?": "reconstruction",
            "top(?:group)?": "top",
            "plots?": "plots",  # plot or plots
            "muon(?:s)?": "muon",  # muon or muons
            # Matches astro or astrophysics
            "astro(?:physics)?": "astro",
            "results?": "results",  # result or results
            "run2": "run2",
            "tutorials?": "tutorials",  # tutorial or tutorials
            "grid": "grid",
            "ibl": "ibl",
            # Allows both "montecarlo" and "monte carlo"
            "monte\\s?carlo": "montecarlo",
            "luminosity": "luminosity",
            "analytics": "analytics",
            "software": "software",
            # Allows "magneticfield", "magnetic field", or "magnetic-field"
            "magnetic[-\\s]?field": "magneticfield",
            "wiki": "wiki",
            # Allow "atlasphysics" or "atlas physics"
            "atlas[-\\s]?physics": "atlasphysics",
            # Allow "atlasdistributedcomputing" or with spaces/dashes between words
            "atlas[-\\s]?distributed[-\\s]?computing": "atlasdistributedcomputing",
            "hdbs": "hdbs",
            "smew": "smew",
            "wmass": "wmass",
            "dibosons": "dibosons",
            "afp": "afp",
            "minimumbias": "minimumbias",
            "bphysics": "bphysics",
            "releasenotes": "releasenotes",
            "tile": "tile",
            "itk": "itk",
            "hlt": "hlt",
            # New additions
            "flow": "flow",
            "tau": "tau",
            "exot": "exot",
            "sm ": "sm",  # Note: space after 'm'
            "pmg": "pmg",
            "derivation": "derivation",
            "forward": "forward",
            "isolation": "isolation",
            "fake": "fake",
            "eft": "eft",
            "production": "production",
            "atlasml": "atlasml",
            "simulation": "simulation",
            "statistics": "statistics",
            "pubcom": "pubcom",
            "recommendation": "recommendation",
            "policy": "policy",
        }

        # Find all matching categories
        categories = []
        for pattern, category in patterns.items():
            if title:
                normalized_title = title.lower()
                if re.search(pattern, normalized_title, re.IGNORECASE):
                    categories.append(category)
            if parent_title:
                normalized_parent = parent_title.lower()
                if re.search(pattern, normalized_parent, re.IGNORECASE):
                    categories.append(category)

        # If no categories found, assign to 'Misc'
        if not categories:
            categories = ["misc"]
        # De Duplication of categories
        categories = list(set(categories))
        return categories


# """
# Metadata we get:
#
# author
# date -> last_modification
# format
# version
# topic_parent
# type
# name
#
# #category
#
#
# Document removed if it contains:
# ---+ Just a Test Area
# %PDFALL% %PDFTHIS%
#
# Document content read from:
# %STARTINCLUDE%
# to
# %STOPINCLUDE%
#
# Trim from this content:
# any line starting: <!--
# any line starting: %RESPONSIBLE%
# any line starting: %REVIEW%
#
#
# Possible Categories:
# misc - uknown/not matched with anything below
#
# ADC/Adc
# ACTS
# AGIS
# AFS
# Ath/Athena
# Atlfast
# Calo
# Conditions
# Cool
# Database
# InnerDetector
# Susy
# SMEW
# Trigger / Trig
# TDAQ
# Jet
# Higgs
# Trt
# Tgc
# Tag / Tagging
# AMA
# Pixel
# MadGraph
# AOD
# AMI
# Tracking / Track / tracker
# Daq
# CSCH
# Sensors
# Computing / compute / comp etc.
# Analysis
# CRC
# Tools
# Athena
# Reconstructing / Reconstruction
# Top
# calorimeter
# Plots
#
# Muon (low)
# Astro (low)
# Results (low)
# Run2 (low)
# Tutorials /tutorial (low)
# Higgs (low)
# database (low)
# TopGroup (low)
# Grid (low)
# IBL
# jets / EtMiss
# MonteCarlo
# Luminosity
# Analytics
# Software
# MagneticField
# wiki
# AtlasProtected
# InDet
# AtlasPhysics
# AtlasDistributedComputing
# None
# HDBS
# WebHome
#
# MuonTriggerCom7TeV
# BTaggingCalibrationsSubgroup
# CoolAthena
#
#
# WE ARE MISSING URL NOW!!
# """


class ATLASTalkVectorStoreCreator(BaseVectorStoreCreator):
    """Class to load and process the ATLAS Talk into standard document form to be
    added to DB.

    Designed to work with eos space: `/eos/atlas/atlascerngroupdisk/phys-mlf/Chatlas/ATLAS_Talk/atlas_discourse_qa_pairs.json`
    """

    def load_documents(self, input_path: Path) -> List[Any]:
        """
        Load documents from ATLAS Discourse form into standard form
        """

        atlas_talk_categories = {
            0: "not-known",
            1: "uncategorized",
            3: "site-feedback",
            5: "recast",
            6: "ml",
            7: "asg",
            8: "asg-containers",
            9: "atlas-software",
            11: "us-tier-3-user-support",
            12: "ftag",
            13: "generators-mg5amc-help",
            14: "trigger-help",
            15: "analysis-software-help",
            16: "athena-help",
            17: "distributed-computing-help",
            18: "statistics-help",
            19: "servicex",
            20: "atlas-phys-searches-ana-preservation-experts",
            21: "git-help",
        }

        documents = []

        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)

        for post in data:
            title = post.get("title", "")
            question = post.get("question", "")
            thread_id = post.get("thread_id", title)
            last_modification = post.get("last_modification", "")
            answers = post.get("answers", [])
            views = post.get("views", 0)
            category_id = post.get("category_id", 0)

            url = f"https://atlas-talk.web.cern.ch/t/{thread_id}"
            category = atlas_talk_categories.get(category_id, "unknown")

            content = f"""Title: {title}

            Question:
            {question}

            Answers:"""

            for i, answer in enumerate(answers):
                content += f"\n\nAnswer {i + 1}:\n{answer.strip()}"

            content = textwrap.dedent(content).strip()

            doc = Document(
                page_content=content,
                metadata={
                    "type": "AtlasTalk",
                    "name": title,
                    "url": url,
                    "last_modification": str(last_modification),
                    "views": views,
                    "category": category,
                },
                id=thread_id,
            )
            documents.append(doc)

        return documents

    def process_document(self, document: Any) -> Document:
        """Already in Document dataclass format on input so can just return."""
        return document


class MkDocsVectorStoreCreator(BaseVectorStoreCreator):
    """Class to load and process the GitLab MkDocs into standard document form to be
    added to DB.

    Requires environment variable `GITLAB_API_KEY` to be set with read access to the API

    Designed to work with eos csv: `/eos/atlas/atlascerngroupdisk/phys-mlf/Chatlas/gitlab_mkdocs_data/gitlab_mkdocs_repos.csv`
    """

    def load_documents(self, input_path: Path) -> List[Any]:
        """
        Load documents from ATLAS Discourse form into standard form

        Checks if last activity in the repo was in teh last 3 years otherwise skips it

        Checks content length is [] otherwise skips it
        """
        self.skipped_docs = []

        API_KEY = os.environ.get("GITLAB_API_KEY")

        headers = {"PRIVATE-TOKEN": API_KEY}

        if not API_KEY:
            raise Exception(
                "Please set your GitLab API key in environment variable: GITLAB_API_KEY"
            )

        documents = []

        try:
            gitlab_docs_csv_full = pd.read_csv(input_path)
            gitlab_docs_csv = gitlab_docs_csv_full[
                gitlab_docs_csv_full["forked"] == False
            ]
        except Exception as e:
            print(
                "Error loading csv data from this path, please check read permissions and existence of the file at "
                "that path."
            )
            raise

        for idx, row in tqdm(gitlab_docs_csv.iterrows(), total=len(gitlab_docs_csv)):
            # Get details
            category = self.get_category(row["repo_group"])
            last_modification = row["last_md_commit_date"]
            last_modification = str(
                datetime.strptime(last_modification, "%Y-%m-%d %H:%M:%S UTC").strftime(
                    "%d-%m-%Y"
                )
            )
            project_id = row["project_id"]

            # Check if last activity is new enough
            last_activity_at = row["last_activity_at"]
            last_act_time = datetime.strptime(last_activity_at, "%Y-%m-%dT%H:%M:%S.%fZ")

            if last_act_time < datetime.now() - timedelta(days=3 * 365):
                # if last activity not in the last 3 years skip it
                self.skipped_docs.append(
                    {
                        "name": row["repo_group"],
                        "reason": "Last activity not in last 3 years",
                    }
                )
                continue

            last_activity_at = str(last_act_time.strftime("%d-%m-%Y"))

            # Need to get URL from API request
            response = self.make_request(row["repo_api_url"], headers=headers)
            base_project_url = response.get("web_url", row["repo_api_url"])

            project_md_files = row["target_md_files"].split("|")

            for md_file in project_md_files:

                file_url = f"{row['repo_api_url']}/repository/files/{urllib.parse.quote(md_file, safe='')}/raw?ref={row['default_branch']}"
                md_file_content = self.make_request(file_url, headers=headers, raw=True)

                # Either 404 or the file contents is empty
                if not md_file_content:
                    self.skipped_docs.append(
                        {
                            "name": f"{row['repo_group']}/{row['repo_name']} :: {'/'.join(md_file.split('/')).replace('.md', '')}",
                            "reason": "md file not found - removed in update?",
                        }
                    )
                    continue
                if not md_file_content.strip() or len(md_file_content.strip()) < 512:
                    self.skipped_docs.append(
                        {
                            "name": f"{row['repo_group']}/{row['repo_name']} :: {'/'.join(md_file.split('/')).replace('.md', '')}",
                            "reason": "File contents in md less than 512 chars",
                        }
                    )
                    continue

                frontend_url = self.get_gitlab_frontend_url(
                    base_project_url, md_file, row["default_branch"]
                )

                name = f"{row['repo_group']}/{row['repo_name']} :: {'/'.join(md_file.split('/')[1:]).replace('.md', '')}"

                doc = Document(
                    page_content=md_file_content.strip(),
                    metadata={
                        "type": "MkDocs",
                        "name": name,
                        "url": frontend_url,
                        "last_modification": last_modification,
                        "category": category,
                        "project_id": project_id,
                        "last_activity_at": last_activity_at,
                        "group": row["repo_group"],
                        "repo_name": row["repo_name"],
                    },
                    id=f"{row['repo_group']} :: {md_file.replace('.md', '')}",
                )
                documents.append(doc)

        return documents

    def process_document(self, document: Any) -> Document:
        """Already in Document dataclass format on input so can just return."""
        return document

    @staticmethod
    def get_category(namespace):
        """
        Get category of a file from the namespace

        Currently this just provides categories for anything with an outer level namespace containing `atlas`
        as otherwise there are ~380 unique categories.
        :param namespace:
        :type namespace:
        :return:
        :rtype:
        """

        split_namespace = namespace.split("/")

        if "atlas" not in split_namespace[0].lower():
            return "misc"

        if (
            split_namespace[0].lower() == "atlas-physics"
            or split_namespace[0].lower() == "atlas-phys"
        ):
            return split_namespace[1]

        return split_namespace[0]

    def make_request(self, url, headers, retries=5, raw=False):
        """
        Make an HTTP request with retry logic and rate limit handling

        Args:
            url (str): The URL to make the request to
            headers (dict): Headers to include in the request
            retries (int, optional): Number of retry attempts. Defaults to 5.
            raw: Is content plain text rather than json

        Returns:
            dict | str: The JSON response from the API

        Raises:
            Exception: If all retries are exhausted or a non-retryable error occurs
        """

        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, headers=headers)

                # Handle rate limiting
                if response.status_code == 429:
                    # Get retry-after header, default if not present
                    retry_after = int(response.headers.get("Retry-After", 30))

                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, 0.1 * retry_after)
                    sleep_time = retry_after + jitter

                    time.sleep(sleep_time)
                    attempt += 1
                    continue

                if response.status_code == 404:
                    # File not found - maybe removed in update
                    if self.verbose:
                        print(
                            f"URL NOT FOUND: {url} - Check if it has been removed from the project"
                        )
                    return

                # Raise errors for non-200 responses
                response.raise_for_status()

                if raw:
                    return response.text
                return response.json()

            except requests.exceptions.RequestException as e:
                # Calculate exponential backoff with jitter
                backoff = math.pow(2, attempt)
                jitter = random.uniform(0, 0.1 * backoff)
                sleep_time = backoff + jitter

                # If this was our last retry, raise the error
                if attempt >= retries - 1:
                    raise Exception(
                        f"Failed after {retries} attempts. Last error: {str(e)}"
                    )

                time.sleep(sleep_time)
                attempt += 1

        raise Exception(f"Failed after {retries} attempts.")

    @staticmethod
    def get_gitlab_frontend_url(base_url, file_path, branch):
        """
        Constructs a GitLab frontend URL for a specific file

        Args:
            base_url (str): The base URL of the GitLab project
            file_path (str): The path to the file within the repository
            branch (str): The branch name (e.g., 'main', 'master')

        Returns:
            str: The complete frontend URL to the file
        """
        return f"{base_url.rstrip('/')}/-/blob/{branch}/{urllib.parse.quote(file_path)}?ref_type=heads"
