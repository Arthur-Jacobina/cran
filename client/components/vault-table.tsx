import { Avatar } from "@/components/ui/avatar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

const vaults = [
  {
    name: "$KWAII",
    symbol: "FLOW",
    price: "$0.87",
    daily: "+$0.89",
    balance: "$425.00",
    liquidity: "high",
    logo: "/flow.webp",
  },
  {
    name: "Ethereum",
    symbol: "ZIR",
    price: "$1.23",
    daily: "+$0.95",
    balance: "$350.00",
    liquidity: "medium",
    logo: "/zircuit.png",
  },
  {
    name: "Ethereum",
    symbol: "BASE",
    price: "$0.95",
    daily: "+$0.65",
    balance: "$250.00",
    liquidity: "high",
    logo: "/base.webp",
  },
  {
    name: "$KWAII",
    symbol: "HBAR",
    price: "$0.07",
    daily: "+$0.35",
    balance: "$150.00",
    liquidity: "medium",
    logo: "/hedera.webp",
  },
  {
    name: "$KWAII",
    symbol: "ZKS",
    price: "$1.45",
    daily: "+$0.42",
    balance: "$150.00",
    liquidity: "high",
    logo: "/zksync.webp",
  },
  {
    name: "$KWAII",
    symbol: "SOM",
    price: "$0.34",
    daily: "+$0.27",
    balance: "$100.00",
    liquidity: "low",
    logo: "/somnia.webp",
  },
]

export function VaultTable() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Vault</TableHead>
          <TableHead>Daily</TableHead>
          <TableHead>Balance</TableHead>
          <TableHead>Likeability</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {vaults.map((vault) => (
          <TableRow key={vault.symbol}>
            <TableCell className="font-medium">
              <div className="flex items-center gap-2">
                <Avatar className="h-6 w-6">
                  <img src={vault.logo} alt={vault.name} />
                </Avatar>
                <div>
                  <div className="font-medium">{vault.name}</div>
                  <div className="text-xs text-muted-foreground">{vault.price}</div>
                </div>
              </div>
            </TableCell>
            <TableCell className="text-green-500">{vault.daily}</TableCell>
            <TableCell>{vault.balance}</TableCell>
            <TableCell>
              <div className="flex gap-1">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div
                    key={i}
                    className={`h-1.5 w-3 rounded-full ${
                      i < (vault.liquidity === "high" ? 3 : vault.liquidity === "medium" ? 2 : 1)
                        ? "bg-primary"
                        : "bg-muted"
                    }`}
                  />
                ))}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

