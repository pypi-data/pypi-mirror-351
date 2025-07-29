{# CorText Graph DB template -#}
PRAGMA synchronous = OFF;
PRAGMA journal_mode = MEMORY;

-- CorText Graph tables
{% for table_name in parsing_data['mappings'] %}
DROP TABLE IF EXISTS [{{table_name}}];
CREATE TABLE [{{table_name}}] (
  file text,
  id integer,
  rank integer,
  parserank integer,
  {% if table_name == 'ISIpubdate' -%}
  data integer
  {% else -%}
  data text
  {% endif -%}
);
{% endfor %}

-- CorText Graph table values
BEGIN TRANSACTION;
{% for table_name in parsing_data['mappings'] -%}
{% for record in parsing_data['mappings'][table_name] -%}
{% if table_name == 'ISIpubdate' -%}
{% set data = record.data -%}
{% else -%}
{% set data = "'" ~ record.data | replace("'", "''") ~ "'" -%}
{% endif -%}
INSERT INTO [{{table_name}}] VALUES ('{{record.file}}', {{record.id}}, {{record.rank}}, {{record.parserank}}, {{data}});
{% endfor %}
{% endfor -%}
END TRANSACTION;

