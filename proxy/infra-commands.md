

```
infra access aws_cli app-editor --app_id help --reason "testing SPI endpoint"
```

```
infra db proxy dev-help-20250128-primary --db-type mysql --access-level admin --flavor dev -r "Zendesk sandbox data migration"
```

```
infra secret put-value --type canva-backend --name contentful-webhook-token --value secret-webhook.txt -- 'backend-component-name=help-rpc' 'application-id=help' 'environment=dev'
```