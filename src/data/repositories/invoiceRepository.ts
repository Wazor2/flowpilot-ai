import { Invoice } from '../models';
import { mockInvoices } from '../demoData';

export class InvoiceRepository {
  private invoices: Invoice[] = [...mockInvoices];

  async getAll(): Promise<Invoice[]> {
    return Promise.resolve(this.invoices);
  }

  async getOverdueInvoices(minAmount?: number): Promise<Invoice[]> {
    let results = this.invoices.filter(inv => inv.status === 'OVERDUE');
    if (minAmount !== undefined) {
      results = results.filter(inv => inv.amount > minAmount);
    }
    return Promise.resolve(results);
  }

  async getById(id: string): Promise<Invoice | undefined> {
    return Promise.resolve(this.invoices.find(inv => inv.id === id));
  }
}
