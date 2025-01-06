from pydantic import ValidationError
import pytest

from app.testing.schemas import DocumentArgs


def test_document_args_validation():
    with pytest.raises(ValidationError):
        DocumentArgs.model_validate_json(json)


json = """{
  "document": [
    {
      "children": [
        "string",
        {
          "children": [
            "string",
            "string",
            {
              "children": [
                "string",
                "string",
                "string",
                {
                  "children": [
                    "string",
                    "string",
                    "string",
                    "string",
                    {
                      "italic": true,
                      "bold": true,
                      "text": "string"
                    },
                    {
                      "children": [
                        {
                          "children": [
                            {
                              "children": [
                                "string",
                                "string",
                                "string",
                                "string",
                                {
                                  "italic": true,
                                  "bold": true,
                                  "text": "string"
                                },
                                "string",
                                {
                                  "children": [
                                    "string"
                                  ],
                                  "type": "ol"
                                }
                              ],
                              "type": "lic"
                            }
                          ],
                          "type": "li"
                        }
                      ],
                      "type": "ul"
                    },
                    {
                      "children": [
                        "string"
                      ],
                      "type": "ol"
                    }
                  ],
                  "type": "a",
                  "url": "string"
                },
                {
                  "italic": true,
                  "bold": true,
                  "text": "string"
                },
                {
                  "children": [
                    {
                      "children": [
                        {
                          "children": [
                            "string",
                            "string",
                            "string",
                            "string",
                            {
                              "italic": true,
                              "bold": true,
                              "text": "string"
                            },
                            "string",
                            {
                              "children": [
                                "string"
                              ],
                              "type": "ol"
                            }
                          ],
                          "type": "lic"
                        }
                      ],
                      "type": "li"
                    }
                  ],
                  "type": "ul"
                },
                {
                  "children": [
                    "string"
                  ],
                  "type": "ol"
                }
              ],
              "type": "spoiler"
            },
            {
              "children": [
                "string",
                "string",
                "string",
                "string",
                {
                  "italic": true,
                  "bold": true,
                  "text": "string"
                },
                {
                  "children": [
                    {
                      "children": [
                        {
                          "children": [
                            "string",
                            "string",
                            "string",
                            "string",
                            {
                              "italic": true,
                              "bold": true,
                              "text": "string"
                            },
                            "string",
                            {
                              "children": [
                                "string"
                              ],
                              "type": "ol"
                            }
                          ],
                          "type": "lic"
                        }
                      ],
                      "type": "li"
                    }
                  ],
                  "type": "ul"
                },
                {
                  "children": [
                    "string"
                  ],
                  "type": "ol"
                }
              ],
              "type": "a",
              "url": "string"
            },
            {
              "italic": true,
              "bold": true,
              "text": "string"
            },
            {
              "children": [
                {
                  "children": [
                    {
                      "children": [
                        "string",
                        "string",
                        "string",
                        "string",
                        {
                          "italic": true,
                          "bold": true,
                          "text": "string"
                        },
                        "string",
                        {
                          "children": [
                            "string"
                          ],
                          "type": "ol"
                        }
                      ],
                      "type": "lic"
                    }
                  ],
                  "type": "li"
                }
              ],
              "type": "ul"
            },
            {
              "children": [
                "string"
              ],
              "type": "ol"
            }
          ],
          "type": "blockquote"
        },
        {
          "children": [
            "string",
            "string",
            "string",
            {
              "children": [
                "string",
                "string",
                "string",
                "string",
                {
                  "italic": true,
                  "bold": true,
                  "text": "string"
                },
                {
                  "children": [
                    {
                      "children": [
                        {
                          "children": [
                            "string",
                            "string",
                            "string",
                            "string",
                            {
                              "italic": true,
                              "bold": true,
                              "text": "string"
                            },
                            "string",
                            {
                              "children": [
                                "string"
                              ],
                              "type": "ol"
                            }
                          ],
                          "type": "lic"
                        }
                      ],
                      "type": "li"
                    }
                  ],
                  "type": "ul"
                },
                {
                  "children": [
                    "string"
                  ],
                  "type": "ol"
                }
              ],
              "type": "a",
              "url": "string"
            },
            {
              "italic": true,
              "bold": true,
              "text": "string"
            },
            {
              "children": [
                {
                  "children": [
                    {
                      "children": [
                        "string",
                        "string",
                        "string",
                        "string",
                        {
                          "italic": true,
                          "bold": true,
                          "text": "string"
                        },
                        "string",
                        {
                          "children": [
                            "string"
                          ],
                          "type": "ol"
                        }
                      ],
                      "type": "lic"
                    }
                  ],
                  "type": "li"
                }
              ],
              "type": "ul"
            },
            {
              "children": [
                "string"
              ],
              "type": "ol"
            }
          ],
          "type": "spoiler"
        },
        {
          "children": [
            "string",
            "string",
            "string",
            "string",
            {
              "italic": true,
              "bold": true,
              "text": "string"
            },
            {
              "children": [
                {
                  "children": [
                    {
                      "children": [
                        "string",
                        "string",
                        "string",
                        "string",
                        {
                          "italic": true,
                          "bold": true,
                          "text": "string"
                        },
                        "string",
                        {
                          "children": [
                            "string"
                          ],
                          "type": "ol"
                        }
                      ],
                      "type": "lic"
                    }
                  ],
                  "type": "li"
                }
              ],
              "type": "ul"
            },
            {
              "children": [
                "string"
              ],
              "type": "ol"
            }
          ],
          "type": "a",
          "url": "string"
        },
        {
          "italic": true,
          "bold": true,
          "text": "string"
        },
        {
          "children": [
            {
              "children": [
                {
                  "children": [
                    "string",
                    "string",
                    "string",
                    "string",
                    {
                      "italic": true,
                      "bold": true,
                      "text": "string"
                    },
                    "string",
                    {
                      "children": [
                        "string"
                      ],
                      "type": "ol"
                    }
                  ],
                  "type": "lic"
                }
              ],
              "type": "li"
            }
          ],
          "type": "ul"
        },
        {
          "children": [
            "string"
          ],
          "type": "ol"
        }
      ],
      "type": "p"
    },
    {
      "children": [
        "string",
        "string",
        {
          "children": [
            "string",
            "string",
            "string",
            {
              "children": [
                "string",
                "string",
                "string",
                "string",
                {
                  "italic": true,
                  "bold": true,
                  "text": "string"
                },
                {
                  "children": [
                    {
                      "children": [
                        {
                          "children": [
                            "string",
                            "string",
                            "string",
                            "string",
                            {
                              "italic": true,
                              "bold": true,
                              "text": "string"
                            },
                            "string",
                            {
                              "children": [
                                "string"
                              ],
                              "type": "ol"
                            }
                          ],
                          "type": "lic"
                        }
                      ],
                      "type": "li"
                    }
                  ],
                  "type": "ul"
                },
                {
                  "children": [
                    "string"
                  ],
                  "type": "ol"
                }
              ],
              "type": "a",
              "url": "string"
            },
            {
              "italic": true,
              "bold": true,
              "text": "string"
            },
            {
              "children": [
                {
                  "children": [
                    {
                      "children": [
                        "string",
                        "string",
                        "string",
                        "string",
                        {
                          "italic": true,
                          "bold": true,
                          "text": "string"
                        },
                        "string",
                        {
                          "children": [
                            "string"
                          ],
                          "type": "ol"
                        }
                      ],
                      "type": "lic"
                    }
                  ],
                  "type": "li"
                }
              ],
              "type": "ul"
            },
            {
              "children": [
                "string"
              ],
              "type": "ol"
            }
          ],
          "type": "spoiler"
        },
        {
          "children": [
            "string",
            "string",
            "string",
            "string",
            {
              "italic": true,
              "bold": true,
              "text": "string"
            },
            {
              "children": [
                {
                  "children": [
                    {
                      "children": [
                        "string",
                        "string",
                        "string",
                        "string",
                        {
                          "italic": true,
                          "bold": true,
                          "text": "string"
                        },
                        "string",
                        {
                          "children": [
                            "string"
                          ],
                          "type": "ol"
                        }
                      ],
                      "type": "lic"
                    }
                  ],
                  "type": "li"
                }
              ],
              "type": "ul"
            },
            {
              "children": [
                "string"
              ],
              "type": "ol"
            }
          ],
          "type": "a",
          "url": "string"
        },
        {
          "italic": true,
          "bold": true,
          "text": "string"
        },
        {
          "children": [
            {
              "children": [
                {
                  "children": [
                    "string",
                    "string",
                    "string",
                    "string",
                    {
                      "italic": true,
                      "bold": true,
                      "text": "string"
                    },
                    "string",
                    {
                      "children": [
                        "string"
                      ],
                      "type": "ol"
                    }
                  ],
                  "type": "lic"
                }
              ],
              "type": "li"
            }
          ],
          "type": "ul"
        },
        {
          "children": [
            "string"
          ],
          "type": "ol"
        }
      ],
      "type": "blockquote"
    },
    {
      "children": [
        "string",
        "string",
        "string",
        {
          "children": [
            "string",
            "string",
            "string",
            "string",
            {
              "italic": true,
              "bold": true,
              "text": "string"
            },
            {
              "children": [
                {
                  "children": [
                    {
                      "children": [
                        "string",
                        "string",
                        "string",
                        "string",
                        {
                          "italic": true,
                          "bold": true,
                          "text": "string"
                        },
                        "string",
                        {
                          "children": [
                            "string"
                          ],
                          "type": "ol"
                        }
                      ],
                      "type": "lic"
                    }
                  ],
                  "type": "li"
                }
              ],
              "type": "ul"
            },
            {
              "children": [
                "string"
              ],
              "type": "ol"
            }
          ],
          "type": "a",
          "url": "string"
        },
        {
          "italic": true,
          "bold": true,
          "text": "string"
        },
        {
          "children": [
            {
              "children": [
                {
                  "children": [
                    "string",
                    "string",
                    "string",
                    "string",
                    {
                      "italic": true,
                      "bold": true,
                      "text": "string"
                    },
                    "string",
                    {
                      "children": [
                        "string"
                      ],
                      "type": "ol"
                    }
                  ],
                  "type": "lic"
                }
              ],
              "type": "li"
            }
          ],
          "type": "ul"
        },
        {
          "children": [
            "string"
          ],
          "type": "ol"
        }
      ],
      "type": "spoiler"
    },
    {
      "children": [
        "string",
        "string",
        "string",
        "string",
        {
          "italic": true,
          "bold": true,
          "text": "string"
        },
        {
          "children": [
            {
              "children": [
                {
                  "children": [
                    "string",
                    "string",
                    "string",
                    "string",
                    {
                      "italic": true,
                      "bold": true,
                      "text": "string"
                    },
                    "string",
                    {
                      "children": [
                        "string"
                      ],
                      "type": "ol"
                    }
                  ],
                  "type": "lic"
                }
              ],
              "type": "li"
            }
          ],
          "type": "ul"
        },
        {
          "children": [
            "string"
          ],
          "type": "ol"
        }
      ],
      "type": "a",
      "url": "string"
    },
    {
      "italic": true,
      "bold": true,
      "text": "string"
    },
    {
      "children": [
        {
          "children": [
            {
              "children": [
                "string",
                "string",
                "string",
                "string",
                {
                  "italic": true,
                  "bold": true,
                  "text": "string"
                },
                "string",
                {
                  "children": [
                    "string"
                  ],
                  "type": "ol"
                }
              ],
              "type": "lic"
            }
          ],
          "type": "li"
        }
      ],
      "type": "ul"
    },
    {
      "children": [
        "string"
      ],
      "type": "ol"
    }
  ]
}"""
