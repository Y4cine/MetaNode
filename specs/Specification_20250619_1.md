JSON-Datei
    metadata (Dict:
        Mandatory:
        - Titel - string
        - Summary - string
        - CreatedBy - string (set automatically)
        - LastModifiedBy - date (set automatically)
        - Version
        - Knot_Schema: FileName or Dict
        - Content_Schema: FileName or dict)
        Optional:
        - additional key-value pairs
    content (Knots: Dict of Dicts)

knot_schema: (defined in metadata of file or in a separate JSON)
    ID
    title
    metadata
    contents: list of content

knot: (actual knot in file)
    according to knot_schema
    additional key-value-pairs

content_schema:
    ID
    title
    content
    metadata
        Mandatory:
        - modified_by: string, automatically set
        - modified: date, automatically set
        - version
        - main: bool
        - renderer: string from ENUM (Text, Markdown, RichText, HTML, - Table, base64 image, SVG, Mermaid, dialog (to be explained - later))
        Optional:
        - lang: string from ENUM (e.g. EN, DE)
        - audience: string from ENUM (e.g. POP, SCI)
        