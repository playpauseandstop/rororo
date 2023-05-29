ISSUE_CREDENTIAL_REQUEST = {
    "credential": {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://www.w3.org/2018/credentials/examples/v1",
        ],
        "id": "http://example.gov/credentials/3732",
        "type": ["VerifiableCredential", "UniversityDegreeCredential"],
        "issuer": "did:example:123",
        "issuanceDate": "2020-03-16T22:37:26.544Z",
        "credentialSubject": {
            "id": "did:example:123",
            "degree": {
                "type": "BachelorDegree",
                "name": "Bachelor of Science and Arts",
            },
        },
    },
    "options": {
        "created": "2020-04-02T18:48:36Z",
        "credentialStatus": {"type": "RevocationList2020Status"},
    },
}

ISSUE_CREDENTIAL_RESPONSE = {
    "verifiableCredential": {
        "proof": {
            "type": "Ed25519Signature2018",
            "created": "2020-04-02T18:28:08Z",
            "verificationMethod": "did:example:123#z6MksHh7qHWvybLg5QTPPdG2DgEjjduBDArV9EF9mRiRzMBN",
            "proofPurpose": "assertionMethod",
            "jws": "eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaXQiOlsiYjY0Il19..YtqjEYnFENT7fNW-COD0HAACxeuQxPKAmp4nIl8jYAu__6IH2FpSxv81w-l5PvE1og50tS9tH8WyXMlXyo45CA",
        },
    }
}
